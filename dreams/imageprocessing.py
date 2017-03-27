import json
from io import BytesIO
from subprocess import PIPE, Popen

import discord
import requests
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from utils.config import load_settings

async def get_img(self, ctx, number, *args):
    try:
        response = requests.get(args[number-1])
        link = args[number-1]
        print("found link")
    except (IndexError, requests.exceptions.RequestException):
        try:
            if ctx.message.mentions[number-1]:
                user = ctx.message.mentions[number-1]
                avatar = 'https://discordapp.com/api/users/{0.id}/avatars/{0.avatar}.jpg'.format(
                    user)
                response = requests.get(avatar)
                link = avatar
                print("found mention")
        except IndexError:
            try:
                if discord.utils.find(lambda r: r.display_name.lower().startswith(str(args[number-1]).lower()), list(ctx.message.server.members)):
                    user = discord.utils.find(lambda r: r.display_name.lower().startswith(
                        str(args[number-1]).lower()), list(ctx.message.server.members))
                    avatar = 'https://discordapp.com/api/users/{0.id}/avatars/{0.avatar}.jpg'.format(
                        user)
                    response = requests.get(avatar)
                    link = avatar
                    print("found name")
                else:
                    raise Exception("flex is a meme")
            except Exception:
                img_urls = []
                async for msg in self.bot.logs_from(ctx.message.channel, before=ctx.message, limit=10):
                    response = None
                    if msg.attachments:
                        img_urls.append(msg.attachments[number-1]['url'])
                    elif msg.embeds:
                        if 'url' in msg.embeds[number-1]:
                            img_urls.append(msg.embeds[number-1]['url'])
                response = requests.get(img_urls[number-1])
                link = img_urls[0]
                print("found image")
    return link

class ImageProcessing:

    def __init__(self, bot):
        self.bot = bot
        self.prefix = load_settings()['prefix']
        self.err_title = load_settings()['error_title']
        self.colourRed = 0xff0000

    @commands.command()
    async def e(self, e: discord.Emoji):
        '''Enlage emote.
        Usage: e :emote:
        '''
        img = Image.open(BytesIO(requests.get(e.url).content)).convert("RGBA")
        final = BytesIO()
        img.save(final, 'png')
        final.seek(0)
        await self.bot.upload(final, filename="{0}.png".format(e.name))

    @commands.command(pass_context=True)
    async def caption(self, ctx, *args):
        '''Caption image
        Usage: caption @user|image text
        '''
        cmd = "caption"
        link = await get_img(self, ctx, 1, *args)
        try:
            text = ' '.join(args)
            if len(ctx.message.mentions):
                text = text.split(' ', 1)[1]
            elif discord.utils.find(lambda r: r.name.startswith(str(args[0])), list(ctx.message.server.members)):
                text = text.split(' ', 1)[1]
            if text == "":
                await self.bot.say(embed=discord.Embed(title=self.err_title, description="Missing caption.", colour=self.colourRed))
            else:
                out = BytesIO()
                img = Image.open(BytesIO(requests.get(link).content)).convert("RGBA")
                img.save(out, 'jpeg')
                out.seek(0)
                proc = Popen(['convert', '-caption', '{}'.format(text), '-', '-background', '#000000', '-bordercolor', '#000000', '-fill', '#ffffff',
                              '-gravity', 'center', '-pointsize', '18', '-polaroid', '0', '-gravity', 'SouthEast', '-chop', '5x5', "img.jpg"], stdin=PIPE)
                proc.communicate(out.read())
                await self.bot.upload("img.jpg")
        except Exception as e:
            await self.bot.say(embed=discord.Embed(title=self.err_title,description=str(e),colour=self.colourRed))

    @commands.command(pass_context=True)
    async def wall(self, ctx, *args):
        '''WE NEED TO BUILD A WALL.
        Usage: wall @user|image
        '''
        cmd = "wall"
        link = await get_img(self, ctx, 1, *args)
        try:
            try:
                spacing = int(args[-1])
            except (ValueError, IndexError):
                spacing = 3
            out = BytesIO()
            img = Image.open(BytesIO(requests.get(link).content)).convert("RGBA")
            img.save(out, 'png')
            out.seek(0)
            COMMAND = r"""convert \( - -resize 128 \) -virtual-pixel tile -background rgba\(0,0,0,0\) -resize 512x512! -distort Perspective "0,0,57,42 0,128,63,130 128,0,140,60 128,128,140,140" img.png"""
            proc = Popen(COMMAND, stdin=PIPE, shell=True)
            proc.communicate(out.read())
            await self.bot.upload("img.png")
        except Exception as e:
            await self.bot.say(embed=discord.Embed(title=self.err_title,description=str(e),colour=self.colourRed))

    @commands.command(pass_context=True)
    async def dots(self, ctx, *args):
        '''Change image into dots.
        Usage: dots @user|image
        '''
        cmd = "dots"
        link = await get_img(self, ctx, 1, *args)
        try:
            out = BytesIO()
            img = Image.open(BytesIO(requests.get(link).content)).convert("RGBA")
            img.save(out, 'png')
            out.seek(0)
            COMMAND = ['convert', '-size', '10x10', 'xc:#00000000', '-draw', 'fill #000000 circle 5,5 2,2', '-write', 'mpr:spots', '+delete', '-', '-size',
                       '{0}x{1}'.format(int(img.size[0]), int(img.size[1])), '-background', '#00000000', 'tile:mpr:spots', '-compose', 'copy_opacity', '-composite', 'img2.png']
            proc = Popen(COMMAND, stdin=PIPE)
            proc.communicate(out.read())
            await self.bot.upload("img2.png")
        except Exception as e:
            await self.bot.say(embed=discord.Embed(title=self.err_title,description=str(e),colour=self.colourRed))

    @commands.command(pass_context=True)
    async def grid(self, ctx, *args):
        '''Change image into grid.
        Usage: grid @user|image spacing
        '''
        cmd = "grid"
        link = await get_img(self, ctx, 1, *args)
        try:
            try:
                spacing = int(args[-1])
            except (ValueError, IndexError):
                spacing = 3
            out = BytesIO()
            img = Image.open(BytesIO(requests.get(link).content)).convert("RGBA")
            img.save(out, 'png')
            out.seek(0)
            COMMAND = r"""convert - -background transparent -crop 10x0 +repage -splice {0}x0 +append -crop 0x10 +repage -splice 0x{0} -append img.png""".format(
                spacing)
            proc = Popen(COMMAND, stdin=PIPE, shell=True)
            proc.communicate(out.read())
            await self.bot.upload("img.png")
        except Exception as e:
            await self.bot.say(embed=discord.Embed(title=self.err_title,description=str(e),colour=self.colourRed))

    @commands.command(pass_context=True)
    async def avatar(self, ctx):
        '''Displays avatar of a given user.
        Usage: avatar @user
        '''
        cmd = "avatar"
        try:
            if ctx.message.mentions[0]:
                user = ctx.message.mentions[0]
                avatar = ctx.message.mentions[0].avatar_url
                await self.bot.say(avatar)
        except IndexError:
            await self.bot.say("No user specified. Please use {0}{1} @username.".format(self.prefix, cmd))

    @commands.command(pass_context=True)
    async def sharpen(self, ctx, *args):
        '''Sharpen image.
        Usage: sharpen @user|image (iterations)
        '''
        cmd = "sharpen"
        link = await get_img(self, ctx, 1, *args)
        try:
            img = Image.open(BytesIO(requests.get(link).content)).convert("RGBA")
            try:
                if int(args[-1]) > 10:
                    iterations = 10
                else:
                    interations = int(args[-1])
                for x in range(1, int(iterations)):
                    img = img.filter(ImageFilter.SHARPEN)
            except (ValueError, IndexError):
                img = img.filter(ImageFilter.SHARPEN)
            final = BytesIO()
            img.save(final, 'png')
            final.seek(0)
            await self.bot.upload(final, filename='{0}.png'.format(cmd))
        except Exception as e:
            await self.bot.say(embed=discord.Embed(title=self.err_title,description=str(e),colour=self.colourRed))

    @commands.command(pass_context=True)
    async def blur(self, ctx, *args):
        '''Blur image.
        Usage: blur @user|image (iterations)
        '''
        cmd = "blur"
        link = await get_img(self, ctx, 1, *args)
        try:
            img = Image.open(BytesIO(requests.get(link).content)).convert("RGBA")
            try:
                if int(args[-1]) > 10:
                    iterations = 10
                else:
                    interations = int(args[-1])
                for x in range(1, int(iterations)):
                    img = img.filter(ImageFilter.BLUR)
            except (ValueError, IndexError):
                img = img.filter(ImageFilter.BLUR)
            final = BytesIO()
            img.save(final, 'png')
            final.seek(0)
            await self.bot.upload(final, filename='{0}.png'.format(cmd))
        except Exception as e:
            await self.bot.say(embed=discord.Embed(title=self.err_title,description=str(e),colour=self.colourRed))

    @commands.command(pass_context=True)
    async def contour(self, ctx, *args):
        '''Enhance contours.
        Usage: contour @user|image (iterations)
        '''
        cmd = "contour"
        link = await get_img(self, ctx, 1, *args)
        try:
            img = Image.open(BytesIO(requests.get(link).content)).convert("RGBA")
            try:
                if int(args[-1]) > 10:
                    iterations = 10
                else:
                    interations = int(args[-1])
                for x in range(1, int(iterations)):
                    img = img.filter(ImageFilter.CONTOUR)
            except (ValueError, IndexError):
                img = img.filter(ImageFilter.CONTOUR)
            final = BytesIO()
            img.save(final, 'png')
            final.seek(0)
            await self.bot.upload(final, filename='{0}.png'.format(cmd))
        except Exception as e:
            await self.bot.say(embed=discord.Embed(title=self.err_title,description=str(e),colour=self.colourRed))

    @commands.command(pass_context=True)
    async def detail(self, ctx, *args):
        '''Enhance details.
        Usage: detail @user|image (iterations)
        '''
        cmd = "detail"
        link = await get_img(self, ctx, 1, *args)
        try:
            img = Image.open(BytesIO(requests.get(link).content)).convert("RGBA")
            try:
                if int(args[-1]) > 10:
                    iterations = 10
                else:
                    interations = int(args[-1])
                for x in range(1, int(iterations)):
                    img = img.filter(ImageFilter.DETAIL)
            except (ValueError, IndexError):
                img = img.filter(ImageFilter.DETAIL)
            final = BytesIO()
            img.save(final, 'png')
            final.seek(0)
            await self.bot.upload(final, filename='{0}.png'.format(cmd))
        except Exception as e:
            await self.bot.say(embed=discord.Embed(title=self.err_title,description=str(e),colour=self.colourRed))

    @commands.command(pass_context=True)
    async def edge(self, ctx, *args):
        '''Enhance edges.
        Usage: edge @user|image (iterations)
        '''
        cmd = "edge"
        link = await get_img(self, ctx, 1, *args)
        try:
            img = Image.open(BytesIO(requests.get(link).content)).convert("RGBA")
            try:
                if int(args[-1]) > 10:
                    iterations = 10
                else:
                    interations = int(args[-1])
                for x in range(1, int(iterations)):
                    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
            except (ValueError, IndexError):
                img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
            final = BytesIO()
            img.save(final, 'png')
            final.seek(0)
            await self.bot.upload(final, filename='{0}.png'.format(cmd))
        except Exception as e:
            await self.bot.say(embed=discord.Embed(title=self.err_title,description=str(e),colour=self.colourRed))

    @commands.command(pass_context=True)
    async def smooth(self, ctx, *args):
        '''Smoothen image.
        Usage: smooth @user|image (iterations)
        '''
        cmd = "smooth"
        link = await get_img(self, ctx, 1, *args)
        try:
            img = Image.open(BytesIO(requests.get(link).content)).convert("RGBA")
            try:
                if int(args[-1]) > 10:
                    iterations = 10
                else:
                    interations = int(args[-1])
                for x in range(1, int(iterations)):
                    img = img.filter(ImageFilter.SMOOTH)
            except (ValueError, IndexError):
                img = img.filter(ImageFilter.SMOOTH)
            final = BytesIO()
            img.save(final, 'png')
            final.seek(0)
            await self.bot.upload(final, filename='{0}.png'.format(cmd))
        except Exception as e:
            await self.bot.say(embed=discord.Embed(title=self.err_title,description=str(e),colour=self.colourRed))

    @commands.command(pass_context=True)
    async def emboss(self, ctx, *args):
        '''Emboss contours.
        Usage: emboss @user|image (iterations)
        '''
        cmd = "emboss"
        link = await get_img(self, ctx, 1, *args)
        try:
            img = Image.open(BytesIO(requests.get(link).content)).convert("RGBA")
            try:
                if int(args[-1]) > 10:
                    iterations = 10
                else:
                    interations = int(args[-1])
                for x in range(1, int(iterations)):
                    img = img.filter(ImageFilter.EMBOSS)
            except (ValueError, IndexError):
                img = img.filter(ImageFilter.EMBOSS)
            final = BytesIO()
            img.save(final, 'png')
            final.seek(0)
            await self.bot.upload(final, filename='{0}.png'.format(cmd))
        except Exception as e:
            await self.bot.say(embed=discord.Embed(title=self.err_title,description=str(e),colour=self.colourRed))

    @commands.command(pass_context=True)
    async def resize(self, ctx, *args):
        '''Resize image.
        Usage: resize @user|image (nearest|bicubic|bilinear|lanczos)
        Filtering is optional.
        '''
        cmd = "resize"
        link = await get_img(self, ctx, 1, *args)
        try:
            img = Image.open(BytesIO(requests.get(link).content)).convert("RGBA")
            try:
                if args[-1].upper() in ("NEAREST", "BICUBIC", "BILINEAR", 'LANCZOS'):
                    size = int(args[-3]), int(args[-2])
                    img = img.resize(size, getattr(Image, args[-1].upper()))
                else:
                    size = int(args[-2]), int(args[-1])
                    img = img.resize(size)
            except (ValueError, IndexError):
                await self.bot.say("Wrong arguments")
            final = BytesIO()
            img.save(final, 'png')
            final.seek(0)
            await self.bot.upload(final, filename='{0}.png'.format(cmd))
        except Exception as e:
            await self.bot.say(embed=discord.Embed(title=self.err_title,description=str(e),colour=self.colourRed))

    @commands.command(pass_context=True,aliases=["cas"])
    async def car(self, ctx, *args):
        '''Content aware resize.
        Usage: car @user|image
        '''
        cmd = "car"
        link = await get_img(self, ctx, 1, *args)
        try:
            img = Image.open(BytesIO(requests.get(link).content)).convert("RGBA")
            try:
                size_x = int(args[-2])
                size_y = int(args[-1])
            except (ValueError, IndexError):
                await self.bot.say("Wrong arguments")
                return
            final = BytesIO()
            out = BytesIO()
            img.save(out, 'png')
            out.seek(0)
            COMMAND = r"""convert - -liquid-rescale {0}x{1}\! img.png""".format(size_x,size_y)
            proc = Popen(COMMAND, stdin=PIPE, shell=True)
            proc.communicate(out.read())
            await self.bot.upload('img.png')
        except Exception as e:
            await self.bot.say(embed=discord.Embed(title=self.err_title,description=str(e),colour=self.colourRed))

    @commands.command(pass_context=True)
    async def rotate(self, ctx, *args):
        '''Rotate image.
        Usage: rotate @user|image angle
        '''
        cmd = "rotate"
        link = await get_img(self, ctx, 1, *args)
        try:
            img = Image.open(BytesIO(requests.get(link).content)).convert("RGBA")
            try:
                img = img.rotate(-int(args[-1]))
            except (ValueError, IndexError):
                img = img
            final = BytesIO()
            img.save(final, 'png')
            final.seek(0)
            await self.bot.upload(final, filename='{0}.png'.format(cmd))
        except Exception as e:
            await self.bot.say(embed=discord.Embed(title=self.err_title,description=str(e),colour=self.colourRed))

    @commands.command(pass_context=True)
    async def flip(self, ctx, *args):
        '''Flip left right
        Usage: flip @user|image
        '''
        cmd = "flip"
        link = await get_img(self, ctx, 1, *args)
        try:
            img = Image.open(BytesIO(requests.get(link).content)).convert("RGBA")
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
            final = BytesIO()
            img.save(final, 'png')
            final.seek(0)
            await self.bot.upload(final, filename='{0}.png'.format(cmd))
        except Exception as e:
            await self.bot.say(embed=discord.Embed(title=self.err_title,description=str(e),colour=self.colourRed))

    @commands.command(pass_context=True)
    async def flop(self, ctx, *args):
        '''Flip top bottom
        Usage: flop @user|image
        '''
        cmd = "flop"
        link = await get_img(self, ctx, 1, *args)
        try:
            img = Image.open(BytesIO(requests.get(link).content)).convert("RGBA")
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
            final = BytesIO()
            img.save(final, 'png')
            final.seek(0)
            await self.bot.upload(final, filename='{0}.png'.format(cmd))
        except Exception as e:
            await self.bot.say(embed=discord.Embed(title=self.err_title,description=str(e),colour=self.colourRed))

    @commands.command(pass_context=True)
    async def meme(self, ctx, *args):
        '''Make a meme
        Usage: meme @user|image top_line|bottom_line
        '''
        cmd = "meme"
        link = await get_img(self, ctx, 1, *args)
        try:
            text = ' '.join(args)
            try:
                response = requests.get(args[0])
                text = text.split(' ', 1)[1]
            except (IndexError, requests.exceptions.RequestException):
                if len(ctx.message.mentions):
                    text = text.split(' ', 1)[1]
                elif discord.utils.find(lambda r: r.display_name.lower().startswith(str(args[0]).lower()), list(ctx.message.server.members)):
                    text = text.split(' ', 1)[1]
            
            if '|' in text:
                split = text.split('|')
                top = split[0]
                bottom = split[1]
            elif ',' in text:
                split = text.split(',')
                top = split[0]
                bottom = split[1]
            else:
                top = text
                bottom = ""
            
            link = requests.get(
                "http://memegen.link/custom/{0}/{1}.jpg?alt={2}".format(top, bottom, link))
            img = Image.open(BytesIO(link.content)).convert("RGBA")
            final = BytesIO()
            img.save(final, 'png')
            final.seek(0)
            await self.bot.upload(final, filename='{0}.png'.format(cmd))
        except Exception as e:
            await self.bot.say(embed=discord.Embed(title=self.err_title,description=str(e),colour=self.colourRed))

    @commands.command(pass_context=True, aliases=['haah'])
    async def mlr(self, ctx, *args):
        '''Mirror left to right.
        Usage: mlr @user|image
        '''
        cmd = "mlr"
        link = await get_img(self, ctx, 1, *args)
        try:
            img = Image.open(BytesIO(requests.get(link).content)).convert("RGBA")
            img2 = img.transpose(Image.FLIP_LEFT_RIGHT)
            x = img.size[0]
            y = img.size[1]
            mask = Image.new(
                "L", (int(img.size[0]), int(img.size[1])), "black")
            maskdraw = ImageDraw.Draw(mask)
            maskdraw.rectangle([(0, 0), (x / 2, y)], fill="white")
            img3 = Image.composite(img, img2, mask)
            final = BytesIO()
            img3.save(final, 'png')
            final.seek(0)
            await self.bot.upload(final, filename='{0}.png'.format(cmd))
        except Exception as e:
            await self.bot.say(embed=discord.Embed(title=self.err_title,description=str(e),colour=self.colourRed))

    @commands.command(pass_context=True, aliases=['waaw'])
    async def mrl(self, ctx, *args):
        '''Mirror right to left.
        Usage: mrl @user|image
        '''
        cmd = "mrl"
        link = await get_img(self, ctx, 1, *args)
        try:
            img = Image.open(BytesIO(requests.get(link).content)).convert("RGBA")
            img2 = img.transpose(Image.FLIP_LEFT_RIGHT)
            x = img.size[0]
            y = img.size[1]
            mask = Image.new(
                "L", (int(img.size[0]), int(img.size[1])), "black")
            maskdraw = ImageDraw.Draw(mask)
            maskdraw.rectangle([(x / 2, 0), (x, y)], fill="white")
            img3 = Image.composite(img, img2, mask)
            final = BytesIO()
            img3.save(final, 'png')
            final.seek(0)
            await self.bot.upload(final, filename='{0}.png'.format(cmd))
        except Exception as e:
            await self.bot.say(embed=discord.Embed(title=self.err_title,description=str(e),colour=self.colourRed))

    @commands.command(pass_context=True, aliases=['hooh'])
    async def mtb(self, ctx, *args):
        '''Mirror top to bottom.
        Usage: mtb @user|image
        '''
        cmd = "mtb"
        link = await get_img(self, ctx, 1, *args)
        try:
            img = Image.open(BytesIO(requests.get(link).content)).convert("RGBA")
            img2 = img.transpose(Image.FLIP_TOP_BOTTOM)
            x = img.size[0]
            y = img.size[1]
            mask = Image.new(
                "L", (int(img.size[0]), int(img.size[1])), "black")
            maskdraw = ImageDraw.Draw(mask)
            maskdraw.rectangle([(0, 0), (x, y / 2)], fill="white")
            img3 = Image.composite(img, img2, mask)
            final = BytesIO()
            img3.save(final, 'png')
            final.seek(0)
            await self.bot.upload(final, filename='{0}.png'.format(cmd))
        except Exception as e:
            await self.bot.say(embed=discord.Embed(title=self.err_title,description=str(e),colour=self.colourRed))

    @commands.command(pass_context=True, aliases=['woow'])
    async def mbt(self, ctx, *args):
        '''Mirror bottom to top.
        Usage: mbt @user|image
        '''
        cmd = "mbt"
        link = await get_img(self, ctx, 1, *args)
        try:
            img = Image.open(BytesIO(requests.get(link).content)).convert("RGBA")
            img2 = img.transpose(Image.FLIP_TOP_BOTTOM)
            x = img.size[0]
            y = img.size[1]
            mask = Image.new(
                "L", (int(img.size[0]), int(img.size[1])), "black")
            maskdraw = ImageDraw.Draw(mask)
            maskdraw.rectangle([(0, y / 2), (x, y)], fill="white")
            img3 = Image.composite(img, img2, mask)
            final = BytesIO()
            img3.save(final, 'png')
            final.seek(0)
            await self.bot.upload(final, filename='{0}.png'.format(cmd))
        except Exception as e:
            await self.bot.say(embed=discord.Embed(title=self.err_title,description=str(e),colour=self.colourRed))

    @commands.command(pass_context=True)
    async def mbltr(self, ctx, *args):
        '''Mirror bottom-left to top-right.
        Usage: mbltr @user|image
        '''
        cmd = "mbltr"
        link = await get_img(self, ctx, 1, *args)
        try:
            img = Image.open(BytesIO(requests.get(link).content)).convert("RGBA")
            img2 = img.transpose(Image.FLIP_LEFT_RIGHT).rotate(90)
            x = img.size[0]
            y = img.size[1]
            if x == y:
                mask = Image.new(
                    "L", (int(img.size[0]), int(img.size[1])), "black")
                maskdraw = ImageDraw.Draw(mask)
                maskdraw.polygon([(0, 0), (0, y), (x, y)], fill="white")
                img3 = Image.composite(img, img2, mask)
                final = BytesIO()
                img3.save(final, 'png')
                final.seek(0)
                await self.bot.upload(final, filename='{0}.png'.format(cmd))
            else:
                await self.bot.say(embed=discord.Embed(title=self.err_title, description="This command only works with square images. Try resize command first.", colour=self.colourRed))
        except Exception as e:
            await self.bot.say(embed=discord.Embed(title=self.err_title,description=str(e),colour=self.colourRed))

    @commands.command(pass_context=True)
    async def mtrbl(self, ctx, *args):
        '''Mirror top-right to bottom-left.
        Usage: mtrbl @user|image
        '''
        cmd = "mtrbl"
        link = await get_img(self, ctx, 1, *args)
        try:
            img = Image.open(BytesIO(requests.get(link).content)).convert("RGBA")
            img2 = img.transpose(Image.FLIP_LEFT_RIGHT).rotate(90)
            x = img.size[0]
            y = img.size[1]
            if x == y:
                mask = Image.new(
                    "L", (int(img.size[0]), int(img.size[1])), "black")
                maskdraw = ImageDraw.Draw(mask)
                maskdraw.polygon([(0, 0), (x, 0), (x, y)], fill="white")
                img3 = Image.composite(img, img2, mask)
                final = BytesIO()
                img3.save(final, 'png')
                final.seek(0)
                await self.bot.upload(final, filename='{0}.png'.format(cmd))
            else:
                await self.bot.say(embed=discord.Embed(title=self.err_title, description="This command only works with square images. Try resize command first.", colour=self.colourRed))
        except Exception as e:
            await self.bot.say(embed=discord.Embed(title=self.err_title,description=str(e),colour=self.colourRed))

    @commands.command(pass_context=True)
    async def mtlbr(self, ctx, *args):
        '''Mirror top-left to bottom-right.
        Usage: mtlbr @user|image
        '''
        cmd = "mtlbr"
        link = await get_img(self, ctx, 1, *args)
        try:
            img = Image.open(BytesIO(requests.get(link).content)).convert("RGBA")
            img2 = img.transpose(Image.FLIP_LEFT_RIGHT).rotate(-90)
            x = img.size[0]
            y = img.size[1]
            if x == y:
                mask = Image.new(
                    "L", (int(img.size[0]), int(img.size[1])), "black")
                maskdraw = ImageDraw.Draw(mask)
                maskdraw.polygon([(0, 0), (0, y), (x, 0)], fill="white")
                img3 = Image.composite(img, img2, mask)
                final = BytesIO()
                img3.save(final, 'png')
                final.seek(0)
                await self.bot.upload(final, filename='{0}.png'.format(cmd))
            else:
                await self.bot.say(embed=discord.Embed(title=self.err_title, description="This command only works with square images. Try resize command first.", colour=self.colourRed))
        except Exception as e:
            await self.bot.say(embed=discord.Embed(title=self.err_title,description=str(e),colour=self.colourRed))

    @commands.command(pass_context=True)
    async def mbrtl(self, ctx, *args):
        '''Mirror bottom-right to top-left.
        Usage: mbrtl @user|image
        '''
        cmd = "mbrtl"
        link = await get_img(self, ctx, 1, *args)
        try:
            img = Image.open(BytesIO(requests.get(link).content)).convert("RGBA")
            img2 = img.transpose(Image.FLIP_LEFT_RIGHT).rotate(-90)
            x = img.size[0]
            y = img.size[1]
            if x == y:
                mask = Image.new(
                    "L", (int(img.size[0]), int(img.size[1])), "black")
                maskdraw = ImageDraw.Draw(mask)
                maskdraw.polygon([(0, y), (x, y), (x, 0)], fill="white")
                img3 = Image.composite(img, img2, mask)
                final = BytesIO()
                img3.save(final, 'png')
                final.seek(0)
                await self.bot.upload(final, filename='{0}.png'.format(cmd))
            else:
                await self.bot.say(embed=discord.Embed(title=self.err_title, description="This command only works with square images. Try resize command first.", colour=self.colourRed))
        except Exception as e:
            await self.bot.say(embed=discord.Embed(title=self.err_title,description=str(e),colour=self.colourRed))

    @commands.command(pass_context=True,aliases=['hearts','gay'])
    async def lovers(self, ctx, *args):
        '''They know they love each other.
        Usage: lovers @user1 @user2
        '''
        cmd = "lovers"
        link = await get_img(self, ctx, 1, *args)
        link2 = await get_img(self, ctx, 2, *args)
        try:
            img = Image.open(BytesIO(requests.get(link).content)).convert("RGBA").resize((128,128),Image.LANCZOS)
            img2 = Image.open(BytesIO(requests.get(link2).content)).convert("RGBA").resize((128,128),Image.LANCZOS)
            comp = Image.new('RGBA',(256,128))
            comp2 = Image.new('RGBA',(256,128))
            comp3 = Image.new('RGBA',(256,128))
            comp4 = Image.new('RGBA',(256,128))
            heart = Image.open("heart_shape.png").convert("RGBA")
            mask = Image.open("heart_shape_mask.png").convert('L')

            img_heart = Image.composite(img, heart, mask).resize((110,110),Image.LANCZOS)
            img2_heart = Image.composite(img2, heart, mask).resize((110,110),Image.LANCZOS)

            comp.paste(heart, (0,0))
            comp2.paste(heart, (100,0))
            ff = Image.alpha_composite(comp, comp2)

            comp3.paste(img_heart, (9,9))
            comp4.paste(img2_heart, (109,9))
            ff2 = Image.alpha_composite(comp3, comp4)

            ff3 = Image.alpha_composite(ff, ff2)

            final = BytesIO()
            ff3.save(final, "png")
            final.seek(0)

            await self.bot.upload(final, filename='{0}.png'.format(cmd))
        except Exception as e:
            await self.bot.say(embed=discord.Embed(title=self.err_title,description=str(e),colour=self.colourRed))


def setup(bot):
    bot.add_cog(ImageProcessing(bot))
