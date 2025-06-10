import google.generativeai as genai

genai.configure(api_key="AIzaSyDt-LMAgZxH9a2qq3qWu_I7_aoGbTKQ7m0")

myfile = genai.upload_file("downloads/tmp_audio.ogg")

model = genai.GenerativeModel("gemini-1.5-flash")

result = model.generate_content(
    [myfile, "\n\n", "Say word to word what in this audio"]
)
print(f"{result.text=}")
