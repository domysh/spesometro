import { Button, Group, Modal, Space } from "@mantine/core"



export const YesOrNoModal = ({ open, onClose, onConfirm, message }:{ open:boolean, onClose?: ()=>void, onConfirm?:()=>void, message:string }) => {
    return <Modal opened={open} onClose={()=>onClose?.()} title="Are you sure?" centered size="sm">
        <Space h="xs" />
        {message}
        <Space h="xl" />
        <Group justify="flex-end">
            <Button color="red" onClick={()=>{
                onConfirm?.()
                onClose?.()
            }}>Yes</Button>
            <Button onClick={onClose}>No</Button>
        </Group>
    </Modal>
}