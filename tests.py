

sites_to_omit = ("youtube", "facebook", "olx", "allegro", "sprzedajemy", "gumtree")


link = "https://youtube.com"

print(link in sites_to_omit)
print(any(x in link for x in sites_to_omit))
