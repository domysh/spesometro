import { useQuery } from "@tanstack/react-query";
import { getRequest } from "./net";
import { board } from "./types";


export const boardsQuery = () => useQuery({
    queryKey:["boards"],
    queryFn: async () => await getRequest("/boards") as board[]
})