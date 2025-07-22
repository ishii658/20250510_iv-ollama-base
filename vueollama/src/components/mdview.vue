<template>
    <div>
      <div v-if="edit">
        <ion-button size="small" @click="toggleEditMode">編集</ion-button>
        <!-- <ion-button size="small" @click="addElement">追加</ion-button> -->
        <!-- <ion-button size="small" @click="delElement">削除</ion-button> -->
      </div>

      <div v-if="isEditMode" class="editor-container">
        <ion-textarea
      class="editarea"
      :value="internalMarkdown"
      @ionInput="updateMarkdown"
      :auto-grow="true"
      :rows="5"
      fill="outline"       
        ></ion-textarea>
      </div>
      <div v-else class="viewer-container">
        <MdPreview
          :modelValue="internalMarkdown"
          :theme="editorTheme"
          :language="editorLanguage"
          :previewTheme="editorPreviewTheme"
          :codeTheme="editorCodeTheme"
          :editorId="editorId"
        />
      </div>        
    </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, defineEmits } from 'vue';
import { IonPage, IonHeader, IonToolbar, IonTitle, IonContent, IonTextarea, IonButton } from '@ionic/vue';
import { MdEditor, MdPreview } from 'md-editor-v3';
import 'md-editor-v3/lib/style.css';
// import screenfull from 'screenfull'; // full screen support
// import html2canvas from 'html2canvas'; // screenshot support

const props = withDefaults(defineProps<{
  markdown: string;
  edit?: boolean;
}>(), {
  edit: true
});

/** update:markdown 更新
 * 　　delelement　要素削除
 *  
 */
const emit = defineEmits(['update:markdown','delelement','addelement']);

const internalMarkdown = ref(props.markdown);
const isEditMode = ref(false); // デフォルトは表示モード

// md-editor-v3 の設定
const editorTheme = 'light'; // または 'dark'
const editorLanguage = 'ja-JP';
const editorPreviewTheme = 'github'; // または 'vuepress', 'mk-cute', 'smart-blue', 'wechat' など
const editorCodeTheme = 'github'; // または 'atom', 'a11y', 'dracula', 'google', 'monokai', 'zenburn' など
const editorId = 'my-editor'; // 任意のユニークなID


// 編集モードの切り替え
const toggleEditMode = () => {
  isEditMode.value = !isEditMode.value;
};

const updateMarkdown = (event: CustomEvent) => {
  internalMarkdown.value = event.detail.value;
  emit('update:markdown', internalMarkdown.value);
};

function addElement(){
  emit('addelement');
}

function delElement(){
  emit('delelement');
}

// 親からのmarkdownプロパティの変更を監視し、internalMarkdownに反映
watch(() => props.markdown, (newValue) => {
  internalMarkdown.value = newValue;
});

// internalMarkdownの変更を親に通知
watch(internalMarkdown, (newValue) => {
  emit('update:markdown', newValue);
});

// 保存処理の例 (編集モード時のみ)
const handleSave = (value: string) => {
  console.log('Markdown saved:', value);
  // ここで保存処理（API送信など）を行うことができます
  emit('update:markdown', value); // 保存時にも親に通知
};

// Mermaidの表示に関する設定はmd-editor-v3が内部的に処理します。
// 特に設定は不要ですが、もし動作しない場合は以下のドキュメントを参照してください。
// https://imzbf.github.io/md-editor-v3/en-US/
onMounted(() => {
  // Mermaidのスクリプトを動的に追加する必要がある場合（通常は不要）
  // const script = document.createElement('script');
  // script.src = 'https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js';
  // document.head.appendChild(script);
});
</script>

<style scoped>
.editor-container, .viewer-container {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
}

/* md-editor-v3 のスタイルを調整する必要がある場合 */
.md-editor-v3 {
  flex-grow: 1;
}

ion-button {
  padding: -10px;
  margin-top: -25px;
  margin-bottom: -10px;
  margin-left:auto;
  font-size:7px;
}
</style>
