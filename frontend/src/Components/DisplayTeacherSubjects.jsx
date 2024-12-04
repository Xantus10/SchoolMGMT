import { Paper, Text, Group } from "@mantine/core";


function DisplayTeacherSubjects({subjects}) {

  return (
    <Group>{subjects.map((sub, ix) => (<Paper p="xs" shadow="sm" key={ix}><Text>{sub[1]}</Text></Paper>))}</Group>
  );
}


export default DisplayTeacherSubjects