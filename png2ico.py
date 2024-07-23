from PIL import Image

# icon.png 파일을 icon.ico로 변환
img = Image.open('app/static/icon.png')
img.save('app/static/icon.ico', format='ICO', sizes=[(32, 32)])

# icon.png 파일을 favicon.ico로 변환
img.save('app/static/favicon.ico', format='ICO', sizes=[(32, 32)])
