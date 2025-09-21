<script lang="tsx">
import { CheckOutlined, FilterOutlined, SyncOutlined } from '@ant-design/icons-vue'
import { Popover } from 'ant-design-vue'
import type { TooltipPlacement } from 'ant-design-vue/es/tooltip'
import { defineComponent, ref } from 'vue'
import type { PropType } from 'vue'

interface FilterOption {
  label: string
  value: string
  checked: boolean
}

interface FilterGroup {
  multiSelect?: boolean
  groupName: string
  options: FilterOption[]
}

export default defineComponent({
  name: 'FilterComp',
  props: {
    filterGroups: {
      type: Array as PropType<FilterGroup[]>,
      default: () => [],
    },
    placement: {
      type: String as PropType<TooltipPlacement>,
      default: 'bottom',
    },
    reset: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['filterChange'],
  setup(props, { emit }) {
    const visible = ref(false)

    const filterGroups = ref<FilterGroup[]>(props.filterGroups)

    const handleFilterChange = (group: FilterGroup, option: FilterOption) => {
      if (!group.multiSelect) {
        group.options.forEach((opt) => {
          opt.checked = false
        })
      }
      option.checked = !option.checked
      console.log(filterGroups.value)
    }

    const clearFilters = () => {
      filterGroups.value.forEach((group) => {
        group.options.forEach((option) => {
          option.checked = false
        })
      })
      visible.value = false
      emit('filterChange', filterGroups.value)
    }

    const filterContent = () => (
      <div class="filter-groups">
        {
          props.reset && (
            <li
              key="reset"
              class="filter-option"
              onClick={() => clearFilters()}
            >
              <span class="inline-block w-4"><SyncOutlined /></span>
              <span class="option-text">清除筛选</span>
            </li>
          )
        }
        {filterGroups.value.map(group => (
          <div key={group.groupName} class="filter-group">
            <div class="filter-group-name">{group.groupName}</div>
            <ul class="filter-options">
              {group.options.map(option => (
                <li
                  key={option.value + option.checked}
                  class={`filter-option ${option.checked ? 'selected' : ''}`}
                  onClick={() => handleFilterChange(group, option)}
                >
                  <span class="inline-block w-4">{option.checked && <CheckOutlined class="check-icon" />}</span>
                  <span class="option-text">{option.label}</span>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    )

    return () => (
      <div class="filter-comp">
        <Popover
          v-model:visible={visible.value}
          trigger="click"
          content={filterContent()}
          placement={props.placement}
        >
          <span class="filter-trigger">
            <FilterOutlined />
          </span>
        </Popover>
      </div>
    )
  },
})
</script>

<style scoped>
.filter-comp {
  display: inline-block;
}

.filter-trigger {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 20px;
  color: var(--color-text-secondary);
}

.filter-groups {
  max-width: 300px;
  width: 100px;
}

.filter-group {
  margin-bottom: 16px;
}

.filter-group-name {
  font-weight: bold;
  margin-bottom: 8px;
}

.filter-options {
  list-style: none;
  padding: 0;
  margin: 0;
}

.filter-option {
  padding: 4px 0;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-option:hover {
  background-color: #716fff0f;
}

.filter-option.selected {
  font-weight: bold;
  color: var(--color-primary);
}

.check-icon {
  color: var(--color-primary);
}

.option-text {
  flex: 1;
}
</style>
