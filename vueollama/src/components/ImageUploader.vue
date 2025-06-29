<template>
  <div
    class="image-uploader"
    @dragover.prevent
    @drop.prevent="handleDrop"
    @paste="handlePaste"
  >
    <ion-button @click="triggerFileInput">画像を選択</ion-button>
    <input
      ref="fileInput"
      type="file"
      accept="image/*"
      @change="handleFileChange"
      hidden
    />
    <p>画像をここにドラッグ＆ドロップ、またはCtrl+Vで貼り付けできます。</p>
  </div>
</template>

<script setup lang="ts">
import { IonButton } from '@ionic/vue'
import { ref } from 'vue'

const emit = defineEmits<{
  (e: 'image-uploaded', base64: string): void
}>()

const fileInput = ref<HTMLInputElement | null>(null)

function triggerFileInput() {
  fileInput.value?.click()
}

function handleFileChange(event: Event) {
  const files = (event.target as HTMLInputElement).files
  if (files && files[0]) {
    convertToBase64(files[0])
  }
}

function handleDrop(event: DragEvent) {
  const files = event.dataTransfer?.files
  if (files && files[0]) {
    convertToBase64(files[0])
  }
}

function handlePaste(event: ClipboardEvent) {
  const items = event.clipboardData?.items
  if (!items) return

  for (const item of items) {
    if (item.type.startsWith('image/')) {
      const file = item.getAsFile()
      if (file) {
        convertToBase64(file)
      }
    }
  }
}

function convertToBase64(file: File) {
  const reader = new FileReader()
  reader.onload = () => {
    const result = reader.result as string
    emit('image-uploaded', result)
  }
  reader.readAsDataURL(file)
}
</script>

<style scoped>
.image-uploader {
  border: 2px dashed #ccc;
  padding: 20px;
  text-align: center;
  border-radius: 10px;
  cursor: pointer;
}
</style>
