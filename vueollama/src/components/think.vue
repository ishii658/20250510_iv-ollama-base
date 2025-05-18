<template>
  <div class="bg-green">
    <button @click="isOpen = !isOpen">
      {{ isOpen ? '閉じる' : '開く' }}
    </button>
    <slot v-if="isOpen"></slot>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const isOpen = ref(false)
</script>

<style scoped>
.bg-green {
  background-color: lightgreen;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
}
</style>