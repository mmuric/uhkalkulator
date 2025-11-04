FROM kivy/buildozer:latest

WORKDIR /home/user/app

# Kopiraj ceo projekat
COPY . /home/user/app

# Pokreni buildozer
CMD ["buildozer", "android", "debug"]
