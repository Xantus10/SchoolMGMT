import LoginForm from "../Components/LoginForm.jsx";
import { Box, Text, Stack, Group, Title, Divider } from '@mantine/core'


function IndexPage() {

  return (
    <>
    <Group justify="center">
      <Stack w={"70%"} bg={"gray.1"} mih={"100vh"}>
        <Group h={"10vh"} bg={"blue.1"} grow>
        <Box p={10}>
          <Title order={1}>SchoolMGMT</Title>
        </Box>
        <Box>
          <Group justify="flex-end" align="center" p={10}>
            <LoginForm />
          </Group>
        </Box>
        </Group>
        <Divider />
        <Text>SchoolMGMT is a web application for managment of schools.</Text>
      </Stack>
    </Group>
    </>
  );

}

export default IndexPage