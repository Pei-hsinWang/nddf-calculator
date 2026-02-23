<template>
  <el-form :model="config" label-position="top" class="config-form">
    <el-divider content-position="left">基本设置</el-divider>
    
    <el-row :gutter="10">
      <el-col :span="12">
        <el-form-item label="ID列名">
          <el-input v-model="config.idCol" placeholder="如: id" />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="年份列名">
          <el-input v-model="config.yearCol" placeholder="如: 年份" />
        </el-form-item>
      </el-col>
    </el-row>

    <el-form-item label="规模报酬类型">
      <el-radio-group v-model="config.isVRS">
        <el-radio :value="false">CRS (规模报酬不变)</el-radio>
        <el-radio :value="true">VRS (规模报酬可变)</el-radio>
      </el-radio-group>
    </el-form-item>

    <el-divider content-position="left">
      投入要素
      <el-button type="primary" size="small" circle @click="addColumn('input')">
        <el-icon><Plus /></el-icon>
      </el-button>
    </el-divider>
    
    <div v-for="(col, index) in config.inputCols" :key="'input-' + index" class="column-row">
      <el-row :gutter="8" align="middle">
        <el-col :span="8">
          <el-select v-model="col.name" placeholder="选择列" size="small" filterable allow-create>
            <el-option v-for="c in availableColumns" :key="c" :label="c" :value="c" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-input-number v-model="col.direction" :min="0" :max="1" :step="1" size="small" controls-position="right" />
        </el-col>
        <el-col :span="8">
          <el-input 
            v-model="col.weightStr" 
            size="small" 
            placeholder="如: 1/4"
            @blur="parseWeight(col)"
          />
        </el-col>
        <el-col :span="2">
          <el-button type="danger" size="small" circle @click="removeColumn('input', index)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </el-col>
      </el-row>
    </div>

    <el-divider content-position="left">
      期望产出
      <el-button type="primary" size="small" circle @click="addColumn('output')">
        <el-icon><Plus /></el-icon>
      </el-button>
    </el-divider>
    
    <div v-for="(col, index) in config.outputCols" :key="'output-' + index" class="column-row">
      <el-row :gutter="8" align="middle">
        <el-col :span="8">
          <el-select v-model="col.name" placeholder="选择列" size="small" filterable allow-create>
            <el-option v-for="c in availableColumns" :key="c" :label="c" :value="c" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-input-number v-model="col.direction" :min="0" :max="1" :step="1" size="small" controls-position="right" />
        </el-col>
        <el-col :span="8">
          <el-input 
            v-model="col.weightStr" 
            size="small" 
            placeholder="如: 1/4"
            @blur="parseWeight(col)"
          />
        </el-col>
        <el-col :span="2">
          <el-button type="danger" size="small" circle @click="removeColumn('output', index)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </el-col>
      </el-row>
    </div>

    <el-divider content-position="left">
      非期望产出
      <el-button type="primary" size="small" circle @click="addColumn('undesired')">
        <el-icon><Plus /></el-icon>
      </el-button>
    </el-divider>
    
    <div v-for="(col, index) in config.undesiredCols" :key="'undesired-' + index" class="column-row">
      <el-row :gutter="8" align="middle">
        <el-col :span="8">
          <el-select v-model="col.name" placeholder="选择列" size="small" filterable allow-create>
            <el-option v-for="c in availableColumns" :key="c" :label="c" :value="c" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-input-number v-model="col.direction" :min="0" :max="1" :step="1" size="small" controls-position="right" />
        </el-col>
        <el-col :span="8">
          <el-input 
            v-model="col.weightStr" 
            size="small" 
            placeholder="如: 1/4"
            @blur="parseWeight(col)"
          />
        </el-col>
        <el-col :span="2">
          <el-button type="danger" size="small" circle @click="removeColumn('undesired', index)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </el-col>
      </el-row>
    </div>

    <div class="column-header">
      <span>列名</span>
      <span>方向</span>
      <span>权重</span>
      <span></span>
    </div>

    <el-divider />

    <div class="weight-summary">
      <el-tag :type="weightSumValid ? 'success' : 'danger'" size="large">
        权重总和: {{ weightSum.toFixed(4) }} {{ weightSumValid ? '(=1)' : '(≠1)' }}
      </el-tag>
    </div>

    <el-button type="primary" @click="applyConfig" style="width: 100%; margin-top: 10px;">
      <el-icon><Check /></el-icon> 应用配置
    </el-button>
  </el-form>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  columns: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['config-change'])

const initCol = (name, direction, weight) => ({
  name,
  direction,
  weight,
  weightStr: formatWeight(weight)
})

const formatWeight = (val) => {
  if (val === 0) return '0'
  if (val === 1) return '1'
  const fractions = [
    [1/2, '1/2'], [1/3, '1/3'], [1/4, '1/4'], [1/5, '1/5'], [1/6, '1/6'],
    [2/3, '2/3'], [3/4, '3/4'], [1/8, '1/8'], [1/12, '1/12']
  ]
  for (const [frac, str] of fractions) {
    if (Math.abs(val - frac) < 0.0001) return str
  }
  return val.toFixed(4)
}

const parseWeight = (col) => {
  const str = col.weightStr.trim()
  if (str.includes('/')) {
    const parts = str.split('/')
    if (parts.length === 2) {
      const num = parseFloat(parts[0])
      const den = parseFloat(parts[1])
      if (!isNaN(num) && !isNaN(den) && den !== 0) {
        col.weight = num / den
        return
      }
    }
  }
  const val = parseFloat(str)
  if (!isNaN(val)) {
    col.weight = val
  }
}

const config = ref({
  inputCols: [
    initCol('L', 1, 1/6),
    initCol('K', 1, 1/6),
    initCol('E', 1, 1/6)
  ],
  outputCols: [
    initCol('Y', 1, 1/4)
  ],
  undesiredCols: [
    initCol('C', 1, 1/4),
    initCol('P', 0, 0)
  ],
  idCol: 'id',
  yearCol: 'year',
  isVRS: false
})

const availableColumns = computed(() => {
  return [...props.columns]
})

const weightSum = computed(() => {
  const allCols = [
    ...config.value.inputCols,
    ...config.value.outputCols,
    ...config.value.undesiredCols
  ]
  return allCols.reduce((sum, col) => sum + (col.weight || 0), 0)
})

const weightSumValid = computed(() => {
  return Math.abs(weightSum.value - 1) < 0.0001
})

const addColumn = (type) => {
  const newCol = { name: '', direction: 1, weight: 0, weightStr: '0' }
  if (type === 'input') {
    config.value.inputCols.push(newCol)
  } else if (type === 'output') {
    config.value.outputCols.push(newCol)
  } else if (type === 'undesired') {
    config.value.undesiredCols.push(newCol)
  }
}

const removeColumn = (type, index) => {
  if (type === 'input' && config.value.inputCols.length > 1) {
    config.value.inputCols.splice(index, 1)
  } else if (type === 'output' && config.value.outputCols.length > 1) {
    config.value.outputCols.splice(index, 1)
  } else if (type === 'undesired' && config.value.undesiredCols.length > 1) {
    config.value.undesiredCols.splice(index, 1)
  } else {
    ElMessage.warning('至少保留一个列')
  }
}

const applyConfig = () => {
  const allCols = [
    ...config.value.inputCols,
    ...config.value.outputCols,
    ...config.value.undesiredCols
  ]
  
  const hasEmpty = allCols.some(col => !col.name)
  if (hasEmpty) {
    ElMessage.warning('请填写所有列名')
    return
  }
  
  if (!weightSumValid.value) {
    ElMessage.error(`权重总和必须为1，当前总和为 ${weightSum.value.toFixed(4)}`)
    return
  }
  
  const outputConfig = {
    inputCols: config.value.inputCols.map(c => ({ name: c.name, direction: c.direction, weight: c.weight })),
    outputCols: config.value.outputCols.map(c => ({ name: c.name, direction: c.direction, weight: c.weight })),
    undesiredCols: config.value.undesiredCols.map(c => ({ name: c.name, direction: c.direction, weight: c.weight })),
    idCol: config.value.idCol,
    yearCol: config.value.yearCol,
    isVRS: config.value.isVRS
  }
  
  emit('config-change', outputConfig)
  ElMessage.success('配置已应用')
}

const setDefaultConfig = (defaultConfig) => {
  if (defaultConfig) {
    config.value = {
      inputCols: defaultConfig.inputCols.map(c => initCol(c.name, c.direction, c.weight)),
      outputCols: defaultConfig.outputCols.map(c => initCol(c.name, c.direction, c.weight)),
      undesiredCols: defaultConfig.undesiredCols.map(c => initCol(c.name, c.direction, c.weight)),
      idCol: defaultConfig.idCol,
      yearCol: defaultConfig.yearCol,
      isVRS: defaultConfig.isVRS
    }
  }
}

watch(() => config.value, () => {
  const outputConfig = {
    inputCols: config.value.inputCols.map(c => ({ name: c.name, direction: c.direction, weight: c.weight })),
    outputCols: config.value.outputCols.map(c => ({ name: c.name, direction: c.direction, weight: c.weight })),
    undesiredCols: config.value.undesiredCols.map(c => ({ name: c.name, direction: c.direction, weight: c.weight })),
    idCol: config.value.idCol,
    yearCol: config.value.yearCol,
    isVRS: config.value.isVRS
  }
  emit('config-change', outputConfig)
}, { deep: true, immediate: true })

defineExpose({ setDefaultConfig })
</script>

<style scoped>
.config-form {
  padding: 10px;
}

.column-row {
  margin-bottom: 8px;
  padding: 8px;
  background: #fafafa;
  border-radius: 4px;
}

.column-header {
  display: flex;
  justify-content: space-between;
  padding: 0 8px;
  margin-bottom: 8px;
  font-size: 12px;
  color: #909399;
}

.column-header span {
  flex: 1;
  text-align: center;
}

.column-header span:last-child {
  flex: 0 0 32px;
}

.el-divider__text {
  display: flex;
  align-items: center;
  gap: 8px;
}

.weight-summary {
  text-align: center;
  padding: 10px 0;
}

:deep(.el-input-number) {
  width: 100%;
}
</style>
