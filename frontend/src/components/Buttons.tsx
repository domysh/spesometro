import { Button } from "@mantine/core"
import { forwardRef } from "react";
import { CgOptions } from "react-icons/cg";
import { FaEdit, FaTrash } from "react-icons/fa";
import { IoMdArrowRoundBack } from "react-icons/io"
import { IoLogOut } from "react-icons/io5"
import { MdAdd } from "react-icons/md";

export const BackButton =  forwardRef<HTMLButtonElement, {onClick?:()=>void}>(({ onClick }, ref) => {
    return <Button ref={ref} color='cyan' size="compact-xs" radius={10} h={35} w={35} onClick={onClick}>
        <IoMdArrowRoundBack size={25} />
    </Button>
})

export const LogoutButton =  forwardRef<HTMLButtonElement,{onClick?:()=>void}>(({ onClick }, ref) => {
    return <Button color='red' ref={ref} size="compact-xs" radius={10} h={35} w={35} onClick={onClick}>
        <IoLogOut size={25} />
    </Button>
})

export const AddButton = forwardRef<HTMLButtonElement, {onClick?:()=>void}>(({ onClick }, ref) => {
    return <Button ref={ref} color='orange' size="compact-xs" radius={10} h={35} w={35} onClick={onClick}>
        <MdAdd size={25} />
    </Button>
})

export const OptionButton = forwardRef<HTMLButtonElement, {onClick?:()=>void}>(({ onClick }, ref) => {
    return <Button ref={ref} color='orange' size="compact-xs" radius={10} h={35} w={35} onClick={onClick}>
        <CgOptions size={25} />
    </Button>
})

export const DeleteButton = forwardRef<HTMLButtonElement, {onClick?:()=>void}>(({ onClick }, ref) => {
    return <Button ref={ref} color='red' size="compact-xs" h={35} w={35} onClick={onClick}>
        <FaTrash size={15} />
    </Button>
})

export const EditButton = forwardRef<HTMLButtonElement, {onClick?:()=>void, disabled?: boolean}>((props, ref) => {
    return <Button ref={ref} color='blue' size="compact-xs" radius={10} h={35} w={35} {...props}>
        <FaEdit size={15} />
    </Button>
})
