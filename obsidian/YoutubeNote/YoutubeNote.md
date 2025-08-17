 `up:` [[0.Map_of_Contents/Home|Home]]

- See also [[YouTube Database]]
    
> [info]+ **Jump Menu**
> 
> - [[YouTube Videos (A–K)]]>     
> - [[YouTube Videos (L–V)]]>     
> - [[YouTube Video (W–Z)]]>     
> - [[YouTube Video Clips 🎥]]
>     
> 
> ^myYouTubeWatchList

> [info] **Vault Info**  
> This section of your vault contains all the notes taken watching YouTube videos that have caught your interest or attention. By actively consuming content you work on progressing further as a life learner.

```dataview  
TABLE WITHOUT ID  
 file.link as "List from Vault",  
 (date(today) - file.cday).day as "Days alive"

FROM "3.Memo/YouTubeNote"

WHERE file.name != "+ HealthyGamerGG"  
AND  
file.name != "HealthyGamerGG"

SORT file.name ASC

LIMIT 90
```
