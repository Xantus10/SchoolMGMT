import { Center, Title, Text, Divider, Stack } from "@mantine/core";


function NotFoundPage() {

  return (
    <>
      <Center h={"100vh"}>
        <Stack align="center">
          <Title order={2}>404 - Not found</Title>
          <Divider />
          <Text>Contact the site's admin for more info</Text>
        </Stack>
      </Center>
    </>
  );

}

export default NotFoundPage