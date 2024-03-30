import { getLoading, useLoading, useToken } from "@/utils"
import { postFormRequest } from "@/utils/net";
import { Box, Button, Group, PasswordInput, Space, TextInput, Title } from "@mantine/core"
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications'

export const LoginProvider = ({ children }: { children:any }) => {

    const [token, setToken] = useToken()
    const setLoading = useLoading()
    const loadingStatus = getLoading()
    const form = useForm({
        initialValues: {
            username: '',
            password: '',
        },
        validate: {
            username: (val) => val == ""? "Username is required" : null,
            password: (val) => val == ""? "Password is required" : null,
        },
    });
    
    if (token){
        return <>{children}</>
    }
    return <Box className="center-flex-col" style={{
        width: "100%",
        height: "100%"
    }}>
        <Title order={1}>Login</Title>
        <Space h="md" />
        <form
            style={{
                width: "80%"
            }} 
            onSubmit={form.onSubmit((values) => {
            setLoading(true)
            postFormRequest("login", {body: values})
            .then( (res) => {
                console.log(res)
                if(res.access_token){
                    setToken(res.access_token)
                }else{
                    notifications.show({
                        title: "Unexpected Error",
                        message: res.detail??res??"Unknown error",
                        color: "red",
                        autoClose: 5000
                    })
                }
            })
            .catch( (err) => {
                notifications.show({
                    title: "Error",
                    message: err.detail??err??"Unknown error",
                    color: "red",
                    autoClose: 5000
                })
            })
            .finally(()=>{
                setLoading(false)
            })
        })}>
            <TextInput
                label="Username"
                placeholder="Your username"
                required
                {...form.getInputProps("username")}
            />
            <Space h="md" />
            <PasswordInput
                
                withAsterisk
                label="Password"
                placeholder="Your password"
                required
                {...form.getInputProps("password")}
            />
            <Space h="md" />
            <Group justify="flex-end" mt="md">
                <Button type="submit" loading={loadingStatus}>Login</Button>
            </Group>
        </form>
    </Box>
}