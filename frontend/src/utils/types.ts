
export type board = {
    id: string,
    name: string,
    categories: category[],
    products: product[],
    members: member[]
}

export type category = {
    id: string,
    name: string
}

export type product = {
    id: string,
    name: string,
    price: number,
    categories: string[]
}

export type member = {
    id: string,
    name: string,
    paid: number,
    categories: string[]
}
export enum Role {
    ADMIN = "admin",
    EDITOR = "editor",
    GUEST = "guest"
}