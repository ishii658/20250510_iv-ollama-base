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
import ImgageUploader from '@/components/ImageUploader.vue'

import mdp from '../components/mdview.vue';

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
  /** LLM think */
  think: string;
  /** LLM問い合わせ中 */
  qBusy: boolean;
  /** 履歴 model: user|モデル名|think */
  history: {msg:string, model:string}[];

  del_toggle: boolean;
  think_toggle: boolean;
  history_toggle: boolean;

  /** 画像 base64 */
  img: string;
}

/** リアクティブな変数 */
const pVal = reactive<pValType>({
  question: '',
  answer: '',
  think: '',
  qBusy: false,
  history: [],
  del_toggle: false,
  think_toggle: false,
  history_toggle: false,
  img:""
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
  pVal.think = '';

  const ollamaServer = new Ollama({host: ollamaServerModel.server}); // サーバーの URL を指定

  const send_messages = [];
  // 問
  // send_messages.push({'role': 'system', 'content': 'あなたはアシスタントです.'})

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

  // 最終質問を追加
  if(pVal.img == ''){
    send_messages.push({'role': 'user', 'content': pVal.question})
  }else{
    send_messages.push({'role': 'user', 'content': pVal.question, 'images': [pVal.img]})
  }

  let think_flag = false
  // modelが qwen3 で think モード出ないときは /no_think をつける
  if(pVal.think_toggle){
    if(ollamaServerModel.model.includes("qwen3")||ollamaServerModel.model.includes("deepseek-r1")||ollamaServerModel.model.includes("magistral:")){
      think_flag = true
    }
  }

  if(think_flag){
    // system message
    send_messages.unshift({'role': 'system', 'content': 'あなたは優秀なアシスタントです. 英語で考え、日本語で回答してください.'})
    // リアクティブな変数に回答を格納するためのオブジェクトを作成
    const response = await ollamaServer.chat({
      model: ollamaServerModel.model,
      messages: send_messages,
      stream: true,
      think: true,
      options: {
         num_ctx: 12000
      }
    });
        // 回答取得
    for await (const part of response) {
      pVal.answer += part.message.content;
      if(part.message.thinking !== undefined)
        pVal.think += part.message.thinking;
    }
  }
  else{
    // system message
    send_messages.unshift({'role': 'system', 'content': 'あなたは優秀なアシスタントです. 日本語で回答してください.'})
    // リアクティブな変数に回答を格納するためのオブジェクトを作成
    const response = await ollamaServer.chat({
      model: ollamaServerModel.model,
      messages: send_messages,
      stream: true,
      think:false,
      options: {
         num_ctx: 12000
      }
    });
    // 回答取得
    for await (const part of response) {
      pVal.answer += part.message.content;
    }
  }


  pVal.qBusy = false;

  // 履歴に追加
  pVal.history.push({msg: pVal.question, model: "user"});

  // think の中身を履歴に追加
  pVal.history.push({msg: pVal.think, model: "think"})

  // 回答を履歴に
  pVal.history.push({msg: pVal.answer, model: ollamaServerModel.model})

  // 回答領域をクリア
  pVal.question = '';
  pVal.answer = '';
  pVal.think = '';
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
  pVal.think = "";
}

// 画像追加
function handleImageUploaded(base64: string): void {
  pVal.img = base64.split(",")[1]
}

</script>

<template>
  <ion-page>
    <ion-header :translucent="true">
      <ion-toolbar>
        <ion-title>Ollama
        <ion-button @click="clearHistory" v-if="!pVal.qBusy" style="margin-top: -2px;">clear</ion-button>
        </ion-title>
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
              <ion-col size="12" class="modelstr" v-if="pVal.history[index].msg !== ''">
                {{ pVal.history[index].model }}
              </ion-col>
              <!-- 過去の履歴 -->
              <ion-col size="12" class="history" v-if="pVal.history[index].msg !== ''">
                <!-- model が user, think, それ以外で分ける. v-if で分ける -->
                <ion-row>
                  <ion-col v-if="pVal.history[index].model === 'user'" class="userstr" size="12" @click="onClickHistory(index)">
                    <!-- <MdPreview :editorId="id" :modelValue="pVal.history[index].msg" language="en-US" /> -->
                    <mdp :markdown="pVal.history[index].msg"></mdp>
                  </ion-col>
                  <ion-col v-else-if="pVal.history[index].model === 'think'" class="thinkstr" size="12" @click="onClickHistory(index)">
                    <think class="think">
                      <!-- <MdPreview :editorId="id" :modelValue="pVal.history[index].msg" language="en-US" /> -->
                      <mdp :markdown="pVal.history[index].msg"></mdp>
                    </think>
                  </ion-col>
                  <ion-col v-else class="otherstr" size="12" @click="onClickHistory(index)">
                    <!-- <MdPreview :editorId="id" :modelValue="pVal.history[index].msg" language="en-US" /> -->
                    <mdp :markdown="pVal.history[index].msg"></mdp>
                  </ion-col>
                </ion-row>
                <!-- <MdEditor :editorId="id" v-model="pVal.history[index].msg" previewOnly language="en-US"/> -->
                <!-- <MdPreview :editorId="id" :modelValue="pVal.history[index].msg" language="en-US" /> -->
                <!-- <MdCatalog :editorId="id" :scrollElement="scrollElement" />         -->
              </ion-col>
            </ion-row>
          </ion-col>

          <ion-col size="12" v-if="pVal.think !== ''">
            <MdPreview :editorId="id" :modelValue="pVal.think" language="en-US" />
          </ion-col>
          <ion-col size="12">
            <MdPreview :editorId="id" :modelValue="pVal.answer" language="en-US" />
            <!-- <MdCatalog :editorId="id" :scrollElement="scrollElement" /> -->
          </ion-col>
          <ion-col size="12">
            <ion-textarea aria-label="query" fill="outline" :auto-grow="true" v-model="pVal.question">
            </ion-textarea>
            <ImgageUploader @image-uploaded="handleImageUploaded"
            v-if="ollamaServerModel.model.includes('gemma3:') || ollamaServerModel.model.includes('qwen2.5vl:')">img</ImgageUploader>
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
