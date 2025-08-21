const bot = BotManager.getCurrentBot();

function extractUrl(text) {  
  const regex = /(https?:\/\/[^\s]+)/g;  
  const found = text.match(regex);  
  return found ? found[0] : null;  
}

function onMessage(msg) {  
  const allowedRooms = ['방이름1', '방이름2'];  
  if (!allowedRooms.includes(msg.room)) {  
    return;  
  }

  if (msg.author.name === '출력제외할봇이름' ) { 
   return; 
  }

  const url = extractUrl(msg.content);  
  if (!url) {  
    return;  
  }

  try {  
    var webhookUrl = 'N8N웹훅주소를 입력하세요';

    org.jsoup.Jsoup.connect(webhookUrl)  
      .header("Content-Type", "application/json")  
      .requestBody(JSON.stringify({  
        "url": url,  
        "room": msg.room,  
        "sender": msg.author.name  
      }))  
      .ignoreContentType(true)  
      .ignoreHttpErrors(true)  
      .timeout(30000)  
      .post();

  } catch (e) {  
    // 오류 발생 시 아무것도 하지 않음  
  }  
}

bot.addListener(Event.MESSAGE, onMessage);