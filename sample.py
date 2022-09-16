a=[{"user_id":3,"tweet":"hi im sam"},{"user_id":1,"tweet":"hi im david"},{"user_id":2,"tweet":"hi im john"}]
tweetlist=[[tweet["tweet"],tweet["tweet"]]for tweet in a if tweet["user_id"]%2!=0]
print(tweetlist)