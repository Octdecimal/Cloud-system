<template>
  <div class="status">
    <h2>任務狀態 (ID: {{ taskId }})</h2>
    <p>目前狀態：<strong>{{ status }}</strong></p>
    <p v-if="assignedNode">執行節點：{{ assignedNode }}</p>
    <p v-if="resultUrl">
      結果完成！<br/>
      <a :href="resultUrl" download>點此下載混音檔</a>
    </p>
  </div>
</template>

<script setup>
import { ref, watch, onUnmounted } from 'vue'
import { useIntervalFn } from '@vueuse/core'  // 也可用 setInterval

const props = defineProps({
  taskId: { type: String, required: true }
})

const status = ref('waiting')
const assignedNode = ref('')
const resultUrl = ref('')
const axios = getCurrentInstance().appContext.config.globalProperties.$axios

// 輪詢 /status
const { pause, resume } = useIntervalFn(async () => {
  try {
    const res = await axios.get('/status')
    const t = res.data.tasks[props.taskId]
    if (!t) return
    status.value = t.status
    if (t.node) assignedNode.value = t.node
    if (t.result) {
      // 建構下載 URL
      resultUrl.value = t.result   // 後端已回傳 /uploads/{id}/{id}.mp3
      pause()
    }
  }
  catch (e) {
    console.error(e)
  }
}, 2000, { immediate: true })

onUnmounted(() => {
  pause()
})
</script>
