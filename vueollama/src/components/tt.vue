<script setup lang="ts">
import { ref } from 'vue'
const isOpen = ref(false)
</script>

<template>
  <div class="bg-green">
    <button @click="isOpen = !isOpen">
      {{ isOpen ? '閉じる' : '開く' }}
    </button>
    <slot v-if="isOpen"></slot>
  </div>
</template>