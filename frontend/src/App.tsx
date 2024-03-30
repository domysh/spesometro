import '@mantine/core/styles.css';
import '@mantine/notifications/styles.css'

import { Notifications } from '@mantine/notifications';
import { AppShell, Box, Burger, Button, LoadingOverlay, MantineProvider, Space, Title } from '@mantine/core';
import { LoginProvider } from './components/LoginProvider';
import { getLoading, useToken } from './utils';
import { DEV_IP_BACKEND } from './utils/net';
import io from 'socket.io-client';
import { useQueryClient } from '@tanstack/react-query';
import { useEffect } from 'react';
import { notifications } from '@mantine/notifications';
import { useDisclosure, useToggle } from '@mantine/hooks';
import { IoLogOut } from "react-icons/io5";

const socket = import.meta.env.DEV?
    io("ws://"+DEV_IP_BACKEND, {transports: ["websocket", "polling"], path:"/sock" }):
    io({transports: ["websocket", "polling"], path:"/sock"})

export default function App() {

  const loadingStatus = getLoading()
  const queryClient = useQueryClient()

  useEffect(()=>{
    socket.on("update", (data) => {
      queryClient.invalidateQueries({ queryKey: data  })
    })
    socket.on("connect_error", (err) => {
      notifications.show({
        title: "Socket.Io connection failed!",
        message: err.message,
        color: "red"
      })
    });
    return () => {
      socket.off("update")
      socket.off("connect_error")
    }
  },[])

  const [opened, { toggle }] = useDisclosure();
  const [_, setToken] = useToken()

  return (
    <MantineProvider defaultColorScheme='dark'>
      <Notifications />
      <LoadingOverlay visible={loadingStatus} zIndex={1000} overlayProps={{ radius: "sm", blur: 2 }} />
      <LoginProvider>
        <AppShell
          header={{ height: 60 }}
          navbar={{
            width: 300,
            breakpoint: 'sm',
            collapsed: { mobile: !opened },
          }}
          padding="md"
        >
          <AppShell.Header>
            <Box style={{
              display: "flex",
              height: "100%",
              alignItems: "center"
            }}>
              <Burger
                opened={opened}
                onClick={toggle}
                hiddenFrom="sm"
                size="sm"
                style={{ marginLeft: "1rem" }}
              />
              <Space w="md" />
              <Title order={2} >
                Spesometro 🛍️
              </Title>
              <Box style={{ flexGrow: 1 }} />
              <Button color='red' size="compact-xs" radius={10} h={35} w={35}
                onClick={() => {
                  setToken("")
                }}
              >
                <IoLogOut size={25} />
              </Button>
              <Space w="md" />
            </Box>
          </AppShell.Header>

          <AppShell.Navbar p="md">
            <div>Navbar</div>
          </AppShell.Navbar>

          <AppShell.Main>Main</AppShell.Main>
        </AppShell>
      </LoginProvider>
    </MantineProvider>
  )
}
