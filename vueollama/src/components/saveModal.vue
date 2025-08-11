<template>
  <ion-content>
    <ion-list>
      <ion-item>
        <ion-label position="stacked">タイトル</ion-label>
        <ion-input v-model="title" />
      </ion-item>
      <ion-item>
        <ion-label position="stacked">説明</ion-label>
        <ion-textarea v-model="description" />
      </ion-item>
    </ion-list>

    <ion-button expand="full" @click="submit">保存</ion-button>
    <ion-button expand="full" color="medium" @click="emit('close')">閉じる</ion-button>
  </ion-content>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import {IonContent, IonButton, IonList, IonItem, IonLabel, IonTextarea, IonInput} from '@ionic/vue'

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'submit', data: { title: string; description: string }): void;
}>();

const title = ref('');
const description = ref('');

const submit = () => {
  emit('submit', {
    title: title.value,
    description: description.value,
  });
  emit('close');
};
</script>
