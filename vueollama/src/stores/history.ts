// stores/category.ts
import axios from 'axios'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useCategoryStore = defineStore('history', () => {
    const history = ref<{ msg: string, model: string }[]>([])

    /** サーバーからメモを取得
     * 
     * @param category カテゴリ
     */
    async function get_memo(category: string, no: number) {
        const res = await axios.get("/api/get_memo", { params: { category: category, memoid: no } })
        if (res.data.status == "error") {
            alert(res.data.msg)
        }
        else {
            history.value = []
            const data: [string, string][] = res.data.result;
            for (let i = 0; i < data.length; i++) {
                history.value.push({ model: data[i][0], msg: data[i][1] })
            }
        }
    }

    return {
        get_memo,
        history
    }
})
