const express = require('express');
const axios = require('axios');
const { App } = require('@slack/bolt')

const app = express();

app.use(express.urlencoded({extended: false}));

app.listen(3000, () => {
    console.log('listening on port 3000!')
})

const slack_app = new App({
  token: 'xoxb-4162327395364-4159893548226-bV52Vy3FGDx2Prs5vwrQH0US',
  signingSecret: 'b8660aa835c195abe26dc289ca9c9832'
});

(async () => {
  const list = await slack_app.client.users.list({
    token: 'xoxb-4162327395364-4159893548226-bV52Vy3FGDx2Prs5vwrQH0US'
  });
 // console.log(list);
  let users = [];
  for (let i = 0; i < list.members.length; i++) {
    if(list.members[i].name !== "slackbot" && list.members[i].name !== "testapi" && list.members[i].name !== "test2"){
        let user = [];
        //console.log("id: " + list.members[i].id);
        user.push(list.members[i].id);
        //console.log("name: " + list.members[i].real_name);
        user.push(list.members[i].real_name);
        //console.log("          ");
        users.push(user);
    }
  }
  //console.log(users);
  
  const readline = require('readline');

  const r1 = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  const r2 = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  let selected = false;
  let selectedIndex = "";
  r1.question(`Enter your name to choose an avatar (using your slack name): `, name =>{
    for (let i = 0; i < users.length; i++){
      if(users[i][1] === name){
        selected = true;
        console.log("       ");
        console.log("Welcome !");
        console.log("ID: " + users[i][0]);
        console.log("Name: " + users[i][1]);
        selectedIndex = i;
        
      }
    }
    if(selected === false) console.log("Make sure you are the registered employee in SAP !");
    r1.close();
    
  })

 
})();

