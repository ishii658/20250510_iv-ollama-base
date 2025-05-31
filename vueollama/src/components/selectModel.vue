// ollama のモデルを選択するための UI コンポーネントを作成します。
<script setup lang="ts">
import {onMounted,reactive,defineEmits, ref} from 'vue';
import {IonButtons, IonSelect, IonSelectOption} from '@ionic/vue';
import {IonToggle} from '@ionic/vue';
import {Ollama} from 'ollama/dist/browser';

/** イベント */
const emit = defineEmits<{(e:'modelSelected', payload:{model:string,server:string}):void}>();

/** リアクティブな変数の定義
 * 
 */
interface pValType {
  models: string[];
}

/**
 * リアクティブな変数の初期化
 */
const pVal = reactive<pValType>({
  models: []
});

const del_toggle = defineModel<boolean>("del_toggle", {default: false})
const think_toggle = defineModel<boolean>("think_toggle",{default: false});
const history_toggle = defineModel<boolean>("history_toggle",{default:false})

/** ollama サーバーからモデルのリストを取得する
 * 
 * @param server 
 */
async function fetchModels(server:Ollama): Promise<string[]> {
  try {
    const modelListObj = await server.list();
    const modelList: string[] = [];
    modelListObj.models.forEach((model) => {
      modelList.push(model.name);
    });
    return modelList;
  } catch (error) {
    console.error('Error fetching models:', error);
    return [];
  }

}

// ollama の接続設定
const ollamaHost = new URL(window.location.origin); // 現在の URL を取得
ollamaHost.port = '11434'; // ポートを変更
const ollamaServer = new Ollama({host: ollamaHost.href}); // サーバーの URL を指定

onMounted(async () => {
  console.log('onMounted');
  // モデルのリストを取得する
  const models = await fetchModels(ollamaServer);
  // リアクティブな変数にコピー
  for(let i=0;i<models.length;i++){
    pVal.models[i] = models[i];
  }
});

/** モデルを選択したときに呼び出される関数  */
function onModelChange(event: CustomEvent)
{
  console.log('onModelChange', event.detail.value);
  emit('modelSelected', {model:event.detail.value, server:ollamaHost.href});
}

</script>

<template>
  <ion-buttons  slot="end">
    <ion-toggle v-model="del_toggle">del</ion-toggle>
    <ion-toggle v-model="think_toggle">think</ion-toggle>
    <ion-toggle v-model="history_toggle">履歴質問</ion-toggle>
    <ion-select label="Model" placeholder="Select a model" @ion-change="onModelChange">
      <!-- モデルのリストを表示する -->
      <ion-select-option  v-for="model in pVal.models" :key="model" :value="model">{{ model }}</ion-select-option>
    </ion-select>
  </ion-buttons>
</template>
<style scoped>
/* Add component-specific styles here */
ion-toggle {
  border: 2px solid #ccc;
  padding: 5px;
  margin-right: 5px;
  border-radius: 5px;
}
</style>