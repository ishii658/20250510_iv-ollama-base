<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-title>メモ一覧</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content class="ion-padding">
      <ion-list>
        <ion-item v-for="(memo, index) in memos" :key="index">
          <ion-label>

              <ion-button @click="()=>{btnclick(memo[0])}">取得</ion-button>
                        <ion-buttons>
              <ion-checkbox v-model="delCheck[index]">確認</ion-checkbox>
              <ion-button shape="round" fill="solid" color="danger" 
                @click="()=>{delClick(index, memo[0])}">削除</ion-button>
            </ion-buttons>

            <h2>{{ memo[1] }}</h2>
            <p>{{ memo[2] }}</p>
          </ion-label>
        </ion-item>
      </ion-list>

      <ion-button router-link="/home">戻る</ion-button>
    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useIonRouter } from '@ionic/vue';
import {IonPage, IonContent, IonHeader, IonToolbar, IonList, IonItem, IonLabel, IonButton, IonButtons, IonCheckbox} from '@ionic/vue'
import axios from 'axios'
import {useCategoryStore} from '../stores/history';
const category = "memo"
const memos = ref([])
const ionRouter = useIonRouter();

/** 確認のチェック */
const delCheck = ref<boolean[]>([])

const store = useCategoryStore()
const {get_memo} = store

async function btnclick(no: number)
{
    get_memo(category, no)
    ionRouter.push("/home")
}

async function fetchMemos() {
  try {
    const res = await axios.get("/get_memo_list",{params:{category: category}}) 
    memos.value = res.data

    // チェックボックス
    delCheck.value = []
    for(let i=0;i<memos.value.length;i++){
      delCheck.value.push(false)
    }
  } catch (error) {
    console.error('メモ取得失敗:', error)
  }
}

/** メモ削除
 * 
 * @param index 
 * @param memoid 
 */
async function delClick(index: number, memoid: number){
  const chk = delCheck.value[index]
  if(!chk){
    alert("チェックボックスにチェックして")
    return
  }

  const res = await axios.get("/del_markdown",
    {params:{category: category, memoid: memoid}}
  )

  fetchMemos()
}

onMounted(() => {
  fetchMemos()
})
</script>