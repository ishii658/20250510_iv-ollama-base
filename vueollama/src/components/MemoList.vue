<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-title>メモ一覧</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content class="ion-padding">
      <ion-list>
        <ion-item v-for="memo in memos" :key="memo[0]">
          <ion-label>
            <ion-button @click="()=>{btnclick(memo[0])}">取得</ion-button>
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
import {IonPage, IonContent, IonHeader, IonToolbar, IonList, IonItem, IonLabel, IonButton} from '@ionic/vue'
import axios from 'axios'
import {useCategoryStore} from '../stores/history';
const category = "memo"
const memos = ref([])
const ionRouter = useIonRouter();

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
  } catch (error) {
    console.error('メモ取得失敗:', error)
  }
}

onMounted(() => {
  fetchMemos()
})
</script>