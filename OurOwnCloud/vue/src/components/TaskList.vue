<template>
  <div>
    <h3>2. 任務列表與下載</h3>
    <table class="table">
      <thead>
        <tr>
          <th>任務 ID</th>
          <th>狀態</th>
          <th>執行節點</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="t in tasks" :key="t.id">
          <td>{{ t.id }}</td>
          <td :class="`status-${t.status}`">{{ t.status }}</td>
          <td>{{ t.node || '—' }}</td>
          <td>
            <!-- Waiting 狀態顯示「開始混音」-->
            <button
              v-if="['new','waiting'].includes(t.status)"
              @click="startMix(t)"
            >開始混音</button>

            <!-- Done 狀態顯示「下載」-->
            <button
              v-else-if="t.status==='done'"
              @click="download(t)"
            >下載</button>

            <!-- 其它狀態不可按 -->
            <span v-else>—</span>

            <!-- 永遠顯示刪除 -->
            <button style="margin-left:8px" @click="deleteTask(t)">
              刪除
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'
import api from '../api.js'

const emit= defineEmits(['refresh'])

const props = defineProps({ tasks: Array })

// 點「開始混音」
async function startMix(task) {
  try {
    const res = await api.post(`/task/start/${task.id}`)
    alert(res.data.message)    // 成功時 alert 出來
    emit('refresh')
  }
  catch (e) {
    console.error(e)
    // 如果有後端 detail，就顯示出來
    const msg = e.response?.data?.detail
              || e.response?.data?.message
              || '派工失敗，請看 console'
    alert(msg)
  }
}

// 點「下載」
function download(task) {
  const url = `${api.defaults.baseURL}/uploads/${task.id}/${task.id}.mp3`
  window.open(url, '_blank')
}

// 點「刪除」
async function deleteTask(task) {
  if (!confirm(`確定要刪除任務 ${task.id} 嗎？`)) return
  try {
    await api.delete(`/remove/${task.id}`)
    emit('refresh')
  }
  catch (e) {
    console.error(e)
    alert("刪除失敗")
  }
}
</script>
