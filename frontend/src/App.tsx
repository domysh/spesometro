import '@mantine/core/styles.css';
import '@mantine/notifications/styles.css'

import { Notifications } from '@mantine/notifications';
import { AppShell, Box, Container, LoadingOverlay, MantineProvider, Space, Title } from '@mantine/core';
import { LoginProvider } from './components/LoginProvider';
import { getLoading, useLoading, useToken } from './utils';
import { DEV_IP_BACKEND } from './utils/net';
import io from 'socket.io-client';
import { useQueryClient } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import { notifications } from '@mantine/notifications';
import { Routes, Route, BrowserRouter } from "react-router-dom";
import { Dashboard } from './components/Dashboard';
import { BoardPage } from './components/BoardPage';
import { LogoutButton } from './components/Buttons';

const socket = import.meta.env.DEV?
    io("ws://"+DEV_IP_BACKEND, {transports: ["websocket", "polling"], path:"/sock" }):
    io({transports: ["websocket", "polling"], path:"/sock"})

export default function App() {

  const loadingStatus = getLoading()
  const queryClient = useQueryClient()
  const setLoading = useLoading()

  useEffect(()=>{
    setLoading(false)
    socket.on("update", (data) => {
      console.log("Update received by socket io:", data)
      queryClient.invalidateQueries({ queryKey: data })
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

  const [_, setToken] = useToken()
  const [header, setHeader] = useState<any>(null)

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
            collapsed: { desktop: true, mobile: true },
          }}
          padding="md"
        >
          <AppShell.Header>
            <Box style={{
              display: "flex",
              height: "100%",
              alignItems: "center"
            }}>
              <Space w="md" />
              <Title order={2} >
                Spesometro 🛍️
              </Title>
              <Box style={{ flexGrow: 1 }} />
              {header}
              <LogoutButton onClick={() => setToken("")} />
              <Space w="md" />
            </Box>
          </AppShell.Header>
          <AppShell.Main>
          <Container>
              <BrowserRouter>
                
                  <Routes>
                    <Route path="/" element={<Dashboard setHeader={setHeader} />} />
                    <Route path="/board/:board_id" element={<BoardPage setHeader={setHeader} />}/>
                    <Route path="/board/:board_id/:screen" element={<BoardPage setHeader={setHeader} />} />
                    <Route path="*" element={<Title order={1}>404 Not Found</Title>} />
                  </Routes>
                
              </BrowserRouter>
            </Container>
          </AppShell.Main>
        </AppShell>
      </LoginProvider>
    </MantineProvider>
  )
}
