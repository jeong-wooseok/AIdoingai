```dataview  
TABLE without ID  
file.link AS "File",
Rating AS "Rating",  
source AS "Video URL",  
channel-name as "Creator",  
tags AS "Tags",  
status AS "Status",  
Date-Added AS "Date Added"  
FROM "3.Memo/YoutubeNote"  
WHERE "File" != "YouTube Database" 
or file.name != "YoutubeNote"  
SORT file.name ASC
```

