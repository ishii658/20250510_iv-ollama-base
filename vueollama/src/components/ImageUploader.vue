<template>
  <div
    class="image-uploader"
    @dragover.prevent
    @drop.prevent="handleDrop"
    @paste="handlePaste"
  >
    <ion-button @click="triggerFileInput">画像を選択
      <p>画像をここにドラッグ＆ドロップ、またはCtrl+Vで貼り付けできます。</p>
    </ion-button>
    <input
      ref="fileInput"
      type="file"
      accept="image/*"
      @change="handleFileChange"
      hidden
    />
    

    <div v-if="uploadedImage" class="uploaded-image-preview">
      <img :src="uploadedImage" alt="Uploaded Image" class="preview-image" />
      <ion-button @click="clearImage" fill="outline" size="small">画像をクリア</ion-button>
    </div>
    <p v-if="isLoading">画像を読み込み中...</p>
  </div>
</template>

<script setup lang="ts">
import { IonButton } from '@ionic/vue'
import { ref } from 'vue'

const emit = defineEmits<{
  (e: 'image-uploaded', base64: string): void;
  (e: 'image-cleared'): void; // 画像がクリアされたことを親に通知するイベントを追加
}>()

const fileInput = ref<HTMLInputElement | null>(null)
const uploadedImage = ref<string | null>(null) // アップロードされた画像のBase64データを保持
const isLoading = ref<boolean>(false); // 画像読み込み中かどうかの状態

/**
 * ファイル選択ダイアログをトリガーします。
 */
function triggerFileInput(): void {
  fileInput.value?.click()
}

/**
 * ファイル入力の変更イベントを処理します。
 * @param event - 変更イベント
 */
function handleFileChange(event: Event): void {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    convertToBase64(file)
  }
}

/**
 * ドラッグ＆ドロップイベントを処理します。
 * @param event - ドラッグイベント
 */
function handleDrop(event: DragEvent): void {
  const file = event.dataTransfer?.files?.[0]
  if (file) {
    convertToBase64(file)
  }
}

/**
 * ペーストイベントを処理します。
 * @param event - クリップボードイベント
 */
function handlePaste(event: ClipboardEvent): void {
  const items = event.clipboardData?.items
  if (!items) return

  for (let i = 0; i < items.length; i++) {
    const item = items[i]
    if (item.type.startsWith('image/')) {
      const file = item.getAsFile()
      if (file) {
        convertToBase64(file)
        break // 最初の画像のみを処理
      }
    }
  }
}

/**
 * FileオブジェクトをBase64文字列に変換し、プレビューに表示し、親コンポーネントにemitします。
 * @param file - 変換するFileオブジェクト
 */
function convertToBase64(file: File): void {
  isLoading.value = true; // 読み込み開始
  const reader = new FileReader()
  reader.onload = () => {
    const result = reader.result as string;
    uploadedImage.value = result; // プレビュー用にBase64データを保存
    emit('image-uploaded', result); // 親コンポーネントにもemit
    isLoading.value = false; // 読み込み終了
  }
  reader.onerror = (error) => {
    console.error('ファイルの読み込み中にエラーが発生しました:', error);
    uploadedImage.value = null; // エラー時は画像をクリア
    isLoading.value = false; // 読み込み終了
    // 必要に応じてエラーメッセージを表示
  };
  reader.readAsDataURL(file)
}

/**
 * アップロードされた画像をクリアし、プレビューを非表示にします。
 */
function clearImage(): void {
  uploadedImage.value = null;
  if (fileInput.value) {
    fileInput.value.value = ''; // input要素の選択状態をリセット
  }
  emit('image-uploaded', ''); // 親コンポーネントにクリアされたことを通知
}
</script>

<style scoped>
.image-uploader {
  border: 2px dashed #ccc;
  padding: 2px;
  text-align: center;
  border-radius: 5px;
  cursor: pointer;
  margin: 2px;
}

.uploaded-image-preview {
  margin-top: 3px;
  padding-top: 2px;
  border-top: 1px solid #eee;
}

.preview-image {
  max-width: 20%;
  height: auto;
  border: 1px solid #ddd;
  border-radius: 8px;
  margin-bottom: 0px;
}

ion-button p{
  padding: 2px;
  margin: 2px;
}
</style>