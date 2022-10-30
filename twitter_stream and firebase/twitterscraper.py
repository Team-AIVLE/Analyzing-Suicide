from Scweet.scweet import scrape
# scrape top tweets with the words 'covid','covid19' and without replies. the process is slower as the interval is
# # smaller (choose an interval that can divide the period of time betwee, start and max date) scrape english top
# # tweets geolocated less than 200 km from Alicante (Spain) Lat=38.3452, Long=-0.481006.
# 
data = scrape(words=['동반자살'], since="2021-01-01", until="2022-10-28", from_account=None, interval=1, headless=False, display_type=False, save_images=False, lang="ko", resume=False, filter_replies=False, proximity=False)