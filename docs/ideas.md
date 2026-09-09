ideas.md

### AI image, audio, video detector for social media.
 - detect ai images, audios, videos and label them, create a model to do that
 - create a browser extension to showcase that. 
 - reverse engineer instagram  through llm, or create a patch like revanced do, to demonstrate how that labeling works on-device 
 
### Fresherr(not a typo - there are two rr - named the project that way )
 - show your offer letter to a AI lawyer trained on Indian employee and labour law.
 - Ai spots the loopholes presented in the offer letter and caution you.
 - AI would generate questions that you could ask hr to gain a better clarity of the situation
 - tells what things are recommended to get in writing

### Didnt name this project
- Ai search for similar software, website or project that the user is querying about.
 - critirea is that it must essentially have free tier. "without credit card" is prioritized 

### Automatic complaint filler
 - filling up govt complaint forms can be tedious
- mostly people dont even know if they can raise complain for a specific issue.
- as this would serve as a thing to do just tthat
- basic idea: finetune a slm, to answer only for the quesestion and let users fill out the form themselves.
 - also could point the user towards a helpline number/customer service, another of that sort that could help the user 

### wo--men
- model that detects male and female characters on the screen.
-  when male mode is activated, it only shows frames with majority of female characters in it. and vice versa
-  just a fun project

### Gov scheme recommender Ai
 - Setup up Rag system with all the gov schemes available for public in india.
 - get necessary info from the users and give them recommendation on what schemes to apply for.
 - what schemes they are eligible for.  

### Athu ethu yethu
- there is a show in tamil, where the anchor would ask a question , and contestant should give answers(just not the questions asked). anchor would ask question again from that give wrong answer, this is done iteratively till a timer goes down. when contestant gives right answer to the question. they lose.
- i am thinking about doing this with llms. both in English and tanglish .
-  would be much better if this was a conversational ai( more better if it realtime)

### synthetic clone
- export WhatsApp chat message and train on model on the person, to talk and respond like them
- remove sensitive personal information, like passwords, api keys, emails, numbers, etc, links, announcements in the chats. so that model is only trained on the way that person speaks.
- ofcourse this is done for educational purposes only

### Deep fake handwriting(salim)
- should research about the feasibility of this project.
- see how to take a handwriting as a reference and try to clone it. 
- like say that user wants to clone their handwriting itself. you ask them to write a paragragh, which contains all possible combinations of how all uppercase and lowercase looks in user handwriting. and the model tries to replicate and clone that handwriting.
- its like voice cloning but for handwriting. 
- after cloning, you write content that user gives you on a document or pdf, in the cloned handwriting\
 
### instagram story patch
- lets say there is a group of friends, and a user followers those group of friends. if one person from that group of friends, posts a story and tags along all those other friends in the group. then when the userr opens instagram , the same story from every friends accounts will be shown on instagram home feed
- it would be frustrating and spamming. we see the metadata of the story and find the mentioned stories and group them.
- why not merge all stories as one story in home feed, and when the story is viewed, you can view members how were taged, this option will be visible as viewed members below the profile picture of the story, minimized it shows +3 members or "and 3 members"
- create a patch like this and use revanced manager to patch instagram
- wow , just had another idea. why not create a platform using ai to generate patch or extra features, features that users wish for. one rule. all these features are supposed to be client side features only. else the model declines 

### partha
- a slm or llm model that can talk with tamil meme template references.
- the model should be talking only in tanglish(transliteration tamil in english) . should hold the natural flow of conversation.
- model should have tamil lyrics knowledge, such that if users speaks or prompt a a bit of song lyrics, it continues the bit more of the remaining part of the song. i have already scraped tamil lyrics, all that is left to do it create train it as corpus and generate qa pairs.
- extra functionality, tool creating for meme template retrieval from the file system. ther would be a folder with all meme templates and we use tool calling to retrieve that faster.
- yellow, pink, purple font, ( i saw a reels saying some quotes and saying "yellow font btw". i dont actualy know what it means. but i guess it represents the emotion, or sincerelity of the way the thing is being said) use different font for different emotion and sincerity 

### ocr for exam paper.
- students lose marks cause most teacher dont fully comprehend that students handwriting. 
- we train a model to extract those different handwriting content, preserving all the formatting it was writing in.
- this will help teacher evaluate the papers easily. and student would actually study and write the answers . instead of focusing on switching between black and blue pens, presenting the paper
- also we automate the entire evaluation pipeline using ai. letting teachers just verify and approve .

### ticket iruka?
- a bucketlist website wher you can tick each thearte off the list of theatres you have watchen a movie in.
- you would tick off every screen , in every theatre and we would rank them.
- like strava , but for theatres 
- import booking history from bookmyshow, district etc, also can put in qr codes.
- but to avoid cheating in this, the qr code data is scanned to see the number of seats booked, and only those no of members can use those qr in the app. after every person has done it, the qr should be invalidate or exhausted as we check it using a db.

### tamil text to speech model
- a light weight tts model both in male and female voice for natural tamil tts. 

### Offtxt
- a react native application , that uses sms to send data, that would otherwise be sent using internet. 
- in india, along with the mobile data person. there is a 100 sms per day included in every ISP's unlimited plan
- people have wifis at home, offices, gyms, hell most of the peoples they go. so recharging a pack with mobile data seems unreasonable.
- if people only recharged with voice only packs, which includes unlimited voice call and 100 sms per day. they can potentially use this app as an alternative for using the internet . this app aims to ulitize those 100 sms which are gone to waste otherwise.
- say you are at a shop, and you have to do a online transcation. only that you dont have net. then you just open this app, scan the payment qr code, and send that to your friends, or family member, who is willing to pay on your behave.
- you could send live location to someone. gps doesn't require internet, so you can just send your coordinates, every 2 or any interval of time, and the receiving end would know your current location. they can be tracking you.
- images can be compressed highly and sent across. you may say this is idea is not feasibility just cuz of this image sending features. but i was testing out a image compressor website called squoosh.app, and i got a 2.92 mb image down to 48.1 kb (48.1kb can be sent thorugh sms ,even if it going to have to be sent in chunks of smses . it can still be sent). all i did was grayscale the image, get the quality down to 10% . use mozjpeg, and use ImageMagick quantization.  image still looks good btw.,
- you can send and receive any qr data. say your friend bought you a metro ticket, he can jus send the qr through the app. the qr content gets converted into text, and the content is sent across, then the qr is rebuild on the receiver end. this can be done for anytinf witrh qr . say movie ticket. etc.
- you can send insta post, without sound(if it is image). etc
- was thinking of a way to build a small tts model and stt model to send and receive voice notes as text. 
- i saw a reels of how, in old nokia mobiles, it had a app called composer . and you could compose music tune using just alphanumberic characters.
- create ai model such that it takes a song tune and ouptuts the alphanumeric characters that can replicate that music tune in nokia composer.
- would be send across this app

### AI person finder in cctv data
- if there is a suspect and there are lot of cctv data, that it is humanly not possible to find that person. we just give the video streams to this ai model and give it a target person to find. and this model does the rest of the work. 

### healthprix halo
- asr model like one used in "the pitt" by Dr.Al hashimi. 
- for doctors

### movie title extractor
- predicting the movie name, from poster . more like extracting. 
- there would be multiple langugaes right how effectively it can understand those languages and does ocr. ocr comes with challenges too, as movie fonts are not the same. It are designed customized for the vibe and plot of the movie.
- there would be artist name, director name and other stuff that is not the title of the movie. os the model should learn to ignore those and focus on the title alow.
-unless if it did from on those stuff. then if could tell apart two films having same name but different people actred and m,ade it.

### Annachi
- AI is extremely patient . so why not flip it over. cakk it "annachi" and make it impatient somehow. giving itt a personality.
-  call it 'annachi' and make it a sugar patient impatient somehow . giving it a personality


