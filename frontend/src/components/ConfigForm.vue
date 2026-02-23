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
          <el-input-number v-model="col.weight" :min="0" :max="1" :step="0.01" size="small" :precision="3" controls-position="right" />
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
          <el-input-number v-model="col.weight" :min="0" :max="1" :step="0.01" size="small" :precision="3" controls-position="right" />
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
          <el-input-number v-model="col.weight" :min="0" :max="1" :step="0.01" size="small" :precision="3" controls-position="right" />
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

    <el-button type="primary" @click="applyConfig" style="width: 100%">
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

const config = ref({
  inputCols: [
    { name: 'L', direction: 1, weight: 0.167 },
    { name: 'K', direction: 1, weight: 0.167 },
    { name: 'E', direction: 1, weight: 0.167 }
  ],
  outputCols: [
    { name: 'Y', direction: 1, weight: 0.25 }
  ],
  undesiredCols: [
    { name: 'C', direction: 1, weight: 0.25 },
    { name: 'P', direction: 0, weight: 0 }
  ],
  idCol: 'id',
  yearCol: 'year',
  isVRS: false
})

const availableColumns = computed(() => {
  const cols = [...props.columns]
  return cols
})

const addColumn = (type) => {
  const newCol = { name: '', direction: 1, weight: 0 }
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
  
  emit('config-change', JSON.parse(JSON.stringify(config.value)))
  ElMessage.success('配置已应用')
}

const setDefaultConfig = (defaultConfig) => {
  if (defaultConfig) {
    config.value = JSON.parse(JSON.stringify(defaultConfig))
  }
}

watch(() => config.value, () => {
  emit('config-change', JSON.parse(JSON.stringify(config.value)))
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

:deep(.el-input-number) {
  width: 100%;
}
</style>
