<script setup lang="ts">
import {reactive} from 'vue';
import {Ollama} from 'ollama/dist/browser';
import { IonContent, IonHeader, IonPage, IonTitle, IonToolbar } from '@ionic/vue';
import { IonGrid, IonRow, IonCol, IonTextarea } from '@ionic/vue';

import { MdPreview, MdCatalog } from 'md-editor-v3';
import 'md-editor-v3/lib/style.css';

import selectModel from '../components/selectModel.vue';

// markdown preview
const id = 'preview-only';
const scrollElement = document.documentElement;

/** リアクティブな変数のための型 */
interface pValType {
  /** LLM への質問 */
  question: string;
  /** LLM の応答 */
  answer: string;
  /** LLM問い合わせ中 */
  qBusy: boolean;
}

/** リアクティブな変数 */
const pVal = reactive<pValType>({
  question: '',
  answer: '',
  qBusy: false,
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
  if(ollamaServerModel.model.includes("qwen3")){
    pVal.question += '\n' + '/no_think'
  }
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
}

</script>

<template>
  <ion-page>
    <ion-header :translucent="true">
      <ion-toolbar>
        <ion-title>Ollama</ion-title>
        <selectModel @modelSelected="onModelSelected"></selectModel>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true">
      <ion-grid>
        <ion-row>
          <ion-col size="12">
            <MdPreview :editorId="id" :modelValue="pVal.answer" language="en-US" />
            <MdCatalog :editorId="id" :scrollElement="scrollElement" />
          </ion-col>
          <ion-col size="12">
            <ion-textarea aria-label="query" fill="outline" :auto-grow="true" v-model="pVal.question">
            </ion-textarea>
          </ion-col>
        </ion-row>
          <ion-col size="12">
            <ion-button expand="block" @click="onSubmit" v-if="!pVal.qBusy" style="margin-top: -20px;">実行</ion-button>
          </ion-col>
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
</style>
