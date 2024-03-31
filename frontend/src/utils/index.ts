import { readLocalStorageValue, readSessionStorageValue, useLocalStorage, useSessionStorage } from "@mantine/hooks";
import { Role } from "./types";

export const useToken = () => useLocalStorage({
    key: "login-token",
    defaultValue: ""
})

export const getToken = (): { userid?: string, exp?: number, role?: Role } => {
    const token = readLocalStorageValue({
        key: "login-token",
        defaultValue: ""
    })
    const splitted = token.split(".")
    return splitted.length >= 2 ? JSON.parse(atob(splitted[1])): {}
}

export const useLoading = () => useSessionStorage({
    key: "glob-loading",
    defaultValue: false
})[1]

export const getLoading = () => readSessionStorageValue({
    key: "glob-loading",
    defaultValue: false
})
