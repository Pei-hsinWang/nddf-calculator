<template>
  <div class="result-table">
    <el-table
      :data="paginatedResults"
      border
      stripe
      size="small"
      max-height="500"
      style="width: 100%"
    >
      <el-table-column :prop="config?.idCol || 'id'" :label="config?.idCol || 'ID'" width="100" fixed />
      <el-table-column :prop="config?.yearCol || 'year'" :label="config?.yearCol || '年份'" width="100" fixed />
      <el-table-column prop="Efficiency_NDDF" label="效率值" width="120">
        <template #default="{ row }">
          {{ formatNumber(row.Efficiency_NDDF) }}
        </template>
      </el-table-column>
      <el-table-column prop="Zeta" label="Zeta" width="120">
        <template #default="{ row }">
          {{ formatNumber(row.Zeta) }}
        </template>
      </el-table-column>
      
      <el-table-column
        v-for="col in priceColumns"
        :key="col"
        :prop="col"
        :label="col"
        min-width="120"
      >
        <template #default="{ row }">
          {{ formatNumber(row[col]) }}
        </template>
      </el-table-column>
      
      <el-table-column
        v-for="col in macColumns"
        :key="col"
        :prop="col"
        :label="col"
        min-width="120"
      >
        <template #default="{ row }">
          {{ formatNumber(row[col]) }}
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="flatResults.length"
        layout="total, sizes, prev, pager, next, jumper"
      />
    </div>

    <el-divider />

    <el-descriptions title="统计摘要" :column="3" border>
      <el-descriptions-item label="总样本数">{{ results.length }}</el-descriptions-item>
      <el-descriptions-item label="平均效率">{{ formatNumber(avgEfficiency) }}</el-descriptions-item>
      <el-descriptions-item label="效率标准差">{{ formatNumber(stdEfficiency) }}</el-descriptions-item>
    </el-descriptions>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  results: {
    type: Array,
    default: () => []
  },
  config: {
    type: Object,
    default: null
  }
})

const currentPage = ref(1)
const pageSize = ref(20)

const flatResults = computed(() => {
  return props.results.map(r => {
    const row = {
      [props.config?.idCol || 'id']: r.id,
      [props.config?.yearCol || 'year']: r.year,
      Efficiency_NDDF: r.Efficiency_NDDF,
      Zeta: r.Zeta
    }
    
    if (r.prices) {
      Object.entries(r.prices).forEach(([key, val]) => {
        row[`Price_${key}`] = val
      })
    }
    
    if (r.mac) {
      Object.entries(r.mac).forEach(([key, val]) => {
        row[`MAC_${key}`] = val
      })
    }
    
    return row
  })
})

const priceColumns = computed(() => {
  if (flatResults.value.length > 0) {
    return Object.keys(flatResults.value[0]).filter(k => k.startsWith('Price_'))
  }
  return []
})

const macColumns = computed(() => {
  if (flatResults.value.length > 0) {
    return Object.keys(flatResults.value[0]).filter(k => k.startsWith('MAC_'))
  }
  return []
})

const paginatedResults = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return flatResults.value.slice(start, end)
})

const avgEfficiency = computed(() => {
  if (props.results.length === 0) return 0
  const sum = props.results.reduce((acc, r) => acc + r.Efficiency_NDDF, 0)
  return sum / props.results.length
})

const stdEfficiency = computed(() => {
  if (props.results.length === 0) return 0
  const avg = avgEfficiency.value
  const squareDiffs = props.results.map(r => Math.pow(r.Efficiency_NDDF - avg, 2))
  return Math.sqrt(squareDiffs.reduce((a, b) => a + b, 0) / props.results.length)
})

const formatNumber = (num) => {
  if (num === null || num === undefined) return '-'
  return Number(num).toFixed(6)
}
</script>

<style scoped>
.result-table {
  padding: 10px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>
