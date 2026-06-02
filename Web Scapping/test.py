
text= "Price: De prijs van dit product is '927' euro en '99' cent"

#extract 927.99 from the text, no text
print(text.split("'"))
price = text.split("'")[1] + "." + text.split("'")[3]
print(price)
