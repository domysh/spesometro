import { readLocalStorageValue, readSessionStorageValue, useLocalStorage, useSessionStorage } from "@mantine/hooks";

export const useToken = () => useLocalStorage({
    key: "login-token",
    defaultValue: ""
})

export const getToken = () => readLocalStorageValue({
    key: "login-token",
    defaultValue: ""
})

export const useLoading = () => useSessionStorage({
    key: "glob-loading",
    defaultValue: false
})[1]

export const getLoading = () => readSessionStorageValue({
    key: "glob-loading",
    defaultValue: false
})