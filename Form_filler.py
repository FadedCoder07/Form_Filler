#%%
import cv2
import pytesseract
from PIL import Image, ImageDraw, ImageFont
import os
import json
import openai

api_key = ""
openai.api_key = api_key
#%%
def replace_word(image_path, target_title, new_content, pil_image):
    image = cv2.imread(image_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    detected_text = pytesseract.image_to_data(gray_image, output_type=pytesseract.Output.DICT)
    
    for i in range(len(detected_text["text"])):
        text = detected_text["text"][i]
        x, y, w, h = detected_text["left"][i], detected_text["top"][i], detected_text["width"][i], detected_text["height"][i]
        
        if target_title in text:
            draw = ImageDraw.Draw(pil_image)
            font = ImageFont.load_default()
            
            new_word_x = x + w + 10  
            new_word_y = y
            
            draw.text((new_word_x, new_word_y), new_content, fill=(255, 0, 0), font=font)
    
        else:
            print(f"'{target_title}' not found.")

json_file_path = "predictions.json"
image_path = "C:/Users/canko/Projeler/Form_Filler/form1.jpg"

with open('json.data', 'r') as f:
    json_data = json.load(f)

pil_image = Image.open(image_path)
prompt = []
titles = []
#%%
for item in json_data["data"]:
    title = item["title"]
    prompt.append(f"Bu resimde {title} ne olabilir?")
    titles.append(title)

prompts = "\n".join(prompt)
#%%
response = openai.ChatCompletion.create(
    model="gpt-4-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompts}
    ],
    max_tokens=150  
)
#%%
if response and 'choices' in response:
    responses = response.choices[0].message['content'].strip().split('\n')
    predictions = dict(zip(titles, responses))

    for title, tahmin in predictions.items():
        replace_word(image_path, title, tahmin, pil_image)
    
    new_image_path = os.path.splitext(image_path)[0] + "_new.jpg"
    pil_image.save(new_image_path)

    with open(json_file_path, 'w') as json_file:
        json.dump(predictions, json_file, indent=4)
