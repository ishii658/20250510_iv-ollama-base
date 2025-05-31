<script setup lang="ts">
import {reactive} from 'vue';
import {Ollama} from 'ollama/dist/browser';
import { IonContent, IonHeader, IonPage, IonTitle, IonToolbar } from '@ionic/vue';
import { IonGrid, IonRow, IonCol, IonTextarea, IonButton } from '@ionic/vue';
import { MdPreview } from 'md-editor-v3';
import 'md-editor-v3/lib/preview.css';
import 'md-editor-v3/lib/style.css';
import {splitThinkContent} from '../util/separateTagContent';
import think from '../components/tt.vue';

import selectModel from '../components/selectModel.vue';

// markdown preview
const id = 'preview-only';
// const scrollElement = document.documentElement;
const scrollElement = document.querySelector('ion-content');

/** リアクティブな変数のための型 */
interface pValType {
  /** LLM への質問 */
  question: string;
  /** LLM の応答 */
  answer: string;
  /** LLM問い合わせ中 */
  qBusy: boolean;
  /** 履歴 model: user|モデル名|think */
  history: {msg:string, model:string}[];

  del_toggle: boolean;
  think_toggle: boolean;
  history_toggle: boolean;
}

/** リアクティブな変数 */
const pVal = reactive<pValType>({
  question: '',
  answer: '',
  qBusy: false,
  history: [],
  del_toggle: false,
  think_toggle: false,
  history_toggle: false,
});

/** ollama サーバーURL とモデル */
interface ollamaServerModelType {
  /** LLM モデル */
  model: string;
  /** サーバー URL */
  server: string;
}

const ohost = new URL(window.location.origin); // 現在の URL を取得
ohost.port = '11434'; // ポートを変更

// 初期状態で選択されているサーバーとモデル
const ollamaServerModel: ollamaServerModelType  = {model: 'qwen3:latest', server: ohost.href};

/** モデルが選択されたときに呼び出される関数  */
function onModelSelected(payload: {model: string, server: string}) {
  // alert('Selected model: ' + payload.model);
  ollamaServerModel.model = payload.model;
  ollamaServerModel.server = payload.server;
}

async function onSubmit() {
  // ボタンを消す
  pVal.qBusy = true;
  // 回答をクリアする
  pVal.answer = '';

  const ollamaServer = new Ollama({host: ollamaServerModel.server}); // サーバーの URL を指定

  const send_messages = [];
  // 問
  send_messages.push({'role': 'system', 'content': 'あなたはアシスタントです.'})

  // 履歴問い合わせのときは、今までのものを入れる
  if(pVal.history_toggle){
    for(let i=0; i<pVal.history.length; i++){
      const row = pVal.history[i];
      const model = row.model;
      if( model == "user" ){
        send_messages.push({'role': 'user', 'content': row.msg});
      }
      else{
        send_messages.push({'role': 'assistant', 'content': row.msg});
      }
    }
  }

  // modelが qwen3 で think モード出ないときは /no_think をつける
  if(!pVal.think_toggle){
    if(ollamaServerModel.model.includes("qwen3")){
      pVal.question += '\n' + '/no_think'
    }
  }

  // 最終質問を追加
  send_messages.push({'role': 'user', 'content': pVal.question})

  // リアクティブな変数に回答を格納するためのオブジェクトを作成
  const response = await ollamaServer.chat({
    model: ollamaServerModel.model,
    messages: send_messages,
    stream: true
  });

  // 回答取得
  for await (const part of response) {
    pVal.answer += part.message.content;
  }

  pVal.qBusy = false;

  // 問から no_think の文字列を削除
  const question_nothink = pVal.question.replace(/\/no_think/g, '');
  const question_think = question_nothink.replace(/\/think/g, '');

  // 回答から think タグの中身を分離
  const sp_answer = splitThinkContent(pVal.answer);

  // 履歴に追加
  pVal.history.push({msg: question_think, model: "user"});

  // think の中身を履歴に追加
  if(sp_answer["thinkContent"] != null){
    pVal.history.push({msg: sp_answer["thinkContent"], model: "think"});
  }
  if(sp_answer["afterThink"] != null){
    pVal.history.push({msg: sp_answer["afterThink"], model: ollamaServerModel.model});
  }
  // pVal.history.push({msg: pVal.answer, model: ollamaServerModel.model});
  

  // 回答領域をクリア
  pVal.question = '';
  pVal.answer = '';
}

function onClickHistory(index: number) {
  if(pVal.del_toggle){
    // 履歴から選択されたメッセージを削除
    pVal.history.splice(index, 1);
  }
}

function clearHistory(){
  pVal.history = [];
  pVal.question = "";
  pVal.answer = "";
}

</script>

<template>
  <ion-page>
    <ion-header :translucent="true">
      <ion-toolbar>
        <ion-title>Ollama</ion-title>
        <selectModel @modelSelected="onModelSelected" 
                     v-model:del_toggle="pVal.del_toggle" 
                     v-model:think_toggle="pVal.think_toggle" 
                     v-model:history_toggle="pVal.history_toggle"
        ></selectModel>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true">
      <ion-grid>
        <ion-row>
          <!-- 履歴のループ -->
          <ion-col size="12">
            <ion-row v-for="(item, index) in pVal.history" :key="index" class="historyarea">
              <!-- モデル名 -->
              <ion-col size="12" class="modelstr">
                {{ pVal.history[index].model }}
              </ion-col>
              <!-- 過去の履歴 -->
              <ion-col size="12" class="history">
                <!-- model が user, think, それ以外で分ける. v-if で分ける -->
                <ion-row>
                  <ion-col v-if="pVal.history[index].model === 'user'" class="userstr" size="12" @click="onClickHistory(index)">
                    <MdPreview :editorId="id" :modelValue="pVal.history[index].msg" language="en-US" />
                  </ion-col>
                  <ion-col v-else-if="pVal.history[index].model === 'think'" class="thinkstr" size="12" @click="onClickHistory(index)">
                    <think class="think">
                      <MdPreview :editorId="id" :modelValue="pVal.history[index].msg" language="en-US" />
                    </think>
                  </ion-col>
                  <ion-col v-else class="otherstr" size="12" @click="onClickHistory(index)">
                    <MdPreview :editorId="id" :modelValue="pVal.history[index].msg" language="en-US" />
                  </ion-col>
                </ion-row>
                <!-- <MdEditor :editorId="id" v-model="pVal.history[index].msg" previewOnly language="en-US"/> -->
                <!-- <MdPreview :editorId="id" :modelValue="pVal.history[index].msg" language="en-US" /> -->
                <!-- <MdCatalog :editorId="id" :scrollElement="scrollElement" />         -->
              </ion-col>
            </ion-row>
          </ion-col>

          <ion-col size="12">
            <MdPreview :editorId="id" :modelValue="pVal.answer" language="en-US" />
            <!-- <MdCatalog :editorId="id" :scrollElement="scrollElement" /> -->
          </ion-col>
          <ion-col size="12">
            <ion-textarea aria-label="query" fill="outline" :auto-grow="true" v-model="pVal.question">
            </ion-textarea>
          </ion-col>
        </ion-row>
        <ion-row>
          <ion-col size="9">
            <ion-button expand="block" @click="onSubmit" v-if="!pVal.qBusy" style="margin-top: -2px;">実行</ion-button>
          </ion-col>
          <ion-col size="3">
            <ion-button expand="block" @click="clearHistory" v-if="!pVal.qBusy" style="margin-top: -2px;">clear</ion-button>
          </ion-col>
        </ion-row>
      </ion-grid>    
    </ion-content>
  </ion-page>
</template>

<style scoped>
#container {
  text-align: center;
  
  position: absolute;
  left: 0;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
}

#container strong {
  font-size: 20px;
  line-height: 26px;
}

#container p {
  font-size: 16px;
  line-height: 22px;
  
  color: #8c8c8c;
  
  margin: 0;
}

#container a {
  text-decoration: none;
}

.modelstr {
  margin-top: 0%;
  padding-top: -0px;
  padding-bottom: 0;
  margin-left: -0px;
  margin-bottom: -2px;
  font-size:x-small;
  background-color: antiquewhite;
  z-index: 200;
}

.history{
  margin-top: -6px;
  z-index: 100;
}

.historyarea {
  border: 2px solid green;
  border-radius: 5px;
  margin-top: 2px;
}

.userstr{
  background-color: aliceblue;
}

.thinkstr{
  background-color: lightyellow;
}

.otherstr{
  background-color: rgb(247, 242, 236);
}

.think{
  padding: 0px;
  margin: 0px;
}
</style>
