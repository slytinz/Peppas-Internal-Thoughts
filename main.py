'''
    Peppa's Internal Thoughts
    Last Updated: 11/15/2024
'''
import discord
from discord.ext import commands
import yaml
import torch
from io import BytesIO
from diffusers import StableDiffusionPipeline, AutoPipelineForText2Image



'''
    Read Config Yaml Data
    
    discord_bot_token: Token can be found on discord developer page (https://discord.com/developers/applications)
    openai_api_key: Token can be found in OpenAI 
    config.yaml: Private yaml file containing private token values
'''
# Read config.yaml and get the openai_key and bot_token
with open("config.yaml", "r") as file:
    config_data = yaml.safe_load(file)

# Set OpenAI API key and Discord keys
# openai.api_key = config_data.get("openai_api_key")
discord_token = config_data.get("discord_bot_token")


'''
    Model List
    
    A list of models for Discord Bot to use
'''
# model_id ="hakurei/waifu-diffusion-v1-4"
# model_id ="gsdf/Counterfeit-V2.5"
# model_id ="nitrosocke/Arcane-Diffusion"
# model_id ="dreamlike-art/dreamlike-diffusion-1.0"
# model_id ="dreamlike-art/dreamlike-anime-1.0"
# model_id ="prompthero/openjourney"
# model_id ="CompVis/stable-diffusion-v1-4"
model_id = "Lykon/DreamShaper"

model = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
# arcane_model = StableDiffusionPipeline.from_pretrained("nitrosocke/Arcane-Diffusion",torch_dtype=torch.float16)
# torch_dtype=torch.float32

'''
    Hardware Check and GPU | CPU usage
'''
# Check if Hardware is Ready
print(torch.cuda.is_available())  # Should print True if CUDA is available
print(torch.cuda.current_device())  # Prints the current device ID
print(torch.cuda.get_device_name(0))  # Prints the name of the GPU
model.to("cuda" if torch.cuda.is_available() else "cpu")
# arcane_model.to("cuda" if torch.cuda.is_available() else "cpu")

'''
    Discord Configurations
'''
# Create an instance of a client
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
# Bot's prefix
bot = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True)
# client = discord.Client(intents=intents)

'''
    Discord Bot Initialization | Connection
'''
@bot.event
async def on_ready():
    try:
        print(f'Logged in as {bot.user}')
    except Exception as e:
        print(f"Error during bot initialization: {e}")
        await bot.close()

'''
    on_message

    Function that will write in the terminal logs the messages received by the Bot
'''
@bot.event
async def on_message(message):
    print(f"Received a message: {message.content}")  # Log every message
    await bot.process_commands(message)  # Ensure commands are processed

'''
    test_command
    
    Function that allows users to use test if bot is receiving data using "!test" command
'''
@bot.command(name="test")
async def test_command(ctx):
    await ctx.send("Test command works!")

'''
    generate_generic_image
    
    Main Function of the Peppa's Internal Thoughts bot. Receives prompts with the use of "!Peppa" command. 
    Prompt is then used by the stable diffusion model to generate images.
'''
@bot.command(name="Peppa")
async def generate_generic_image(ctx, *, prompt: str = None):
    if not prompt:
        await ctx.send("MEOW! Bad Kitty! Please provide a prompt for the image generation. Examples prompts can be found: https://prompthero.com/openjourney-prompts?utm_source=huggingface&utm_medium=referral\n\n Current Model being used: https://civitai.com/models/4384/dreamshaper")
        return
    
    # Initial message indicating progress
    progress_message = await ctx.send(f"Generating your image {ctx.author.mention}, please wait...")
    
    try:
        image = model(prompt).images[0]
        
        # Setup image to be sent
        image_bytes = BytesIO()
        image = image.resize((512, 512))
        image.save(image_bytes, format="PNG", optimize=True)
        image_bytes.seek(0)
        
        # Check Image size
        if len(image_bytes.getvalue()) > 8 * 1024 * 1024:
            print("The generated image exceeds Discord's file size limit.")
            await ctx.send("Something went wrong during image generation.")
            raise discord.HTTPException("Image Size exceeds Discord limitations")
        
        # Send Image to Discord
        await ctx.send(file=discord.File(image_bytes, filename="generated_image.png"))
        await progress_message.delete()
        
        print("Image successfully sent to Discord.")
    
    # Handles Generic Errors
    except Exception as e:
      await progress_message.edit(content="Something went wrong during image generation.")
      print(f"Error has occured: {e}")
    # Handles Discord Errors
    except discord.HTTPException as e:
        print(f"Failed to send image to Discord: {e}")
        
        
'''
    generate_arcane_image
    
    Main Function of the Peppa's Internal Thoughts bot. Receives prompts with the use of "!LOL" command. 
    Prompt is then used by the stable diffusion model to generate images.
'''
# @bot.command(name="LOL")
# async def generate_arcane_image(ctx, *, prompt: str = None):
#     if not prompt:
#         await ctx.send("MEOW! Bad Kitty! Please provide a prompt for the image generation. Add 'arcane style' for some some flair")
#         return
    
#     # Initial message indicating progress
#     progress_message = await ctx.send(f"Generating your image {ctx.author.mention}, please wait...")
    
#     try:
#         image = arcane_model(prompt).images[0]
        
#         # Setup image to be sent
#         image_bytes = BytesIO()
#         image = image.resize((512, 512))
#         image.save(image_bytes, format="PNG", optimize=True)
#         image_bytes.seek(0)
        
#         # Check Image size
#         if len(image_bytes.getvalue()) > 8 * 1024 * 1024:
#             print("The generated image exceeds Discord's file size limit.")
#             await ctx.send("Something went wrong during image generation.")
#             raise discord.HTTPException("Image Size exceeds Discord limitations")
        
#         # Send Image to Discord
#         await ctx.send(file=discord.File(image_bytes, filename="generated_image.png"))
#         await progress_message.delete()
        
#         print("Image successfully sent to Discord.")
    
#     # Handles Generic Errors
#     except Exception as e:
#       await progress_message.edit(content="Something went wrong during image generation.")
#       print(f"Error has occured: {e}")
#     # Handles Discord Errors
#     except discord.HTTPException as e:
#         print(f"Failed to send image to Discord: {e}")

# Run the bot
bot.run(discord_token)

# TODO: Timeout code
# import asyncio
# try:
#     await asyncio.wait_for(ctx.send(file=discord.File(image_bytes, filename="generated_image.png")), timeout=10)
# except asyncio.TimeoutError:
#     await ctx.send("Failed to send the image within the timeout period.")
