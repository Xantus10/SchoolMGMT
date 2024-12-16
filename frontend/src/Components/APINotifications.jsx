import { notifications } from '@mantine/notifications'
import { BiCheckCircle, BiErrorAlt } from "react-icons/bi";


export function GetNotification(responseData) {
  switch (responseData.status) {
    case 401:
      notifications.show({
        title: 'Unauthorized',
        message: '',
        color: 'red.9',
        icon: <BiErrorAlt />
      })
      break;
    case 403:
      notifications.show({
        title: 'Not logged in!',
        message: '',
        color: 'red.9',
        icon: <BiErrorAlt />
      })
      break;
  }
}

export function PostNotification(responseData) {
  switch (responseData.status) {
    case 200:
      notifications.show({
        title: 'Done',
        message: '',
        color: 'lime.8',
        icon: <BiCheckCircle />
      })
      break;
    case 401:
      notifications.show({
        title: 'You are not logged in or your session has expired!',
        message: '',
        color: 'red.9',
        icon: <BiErrorAlt />
      })
      break;
    case 403:
      notifications.show({
        title: 'You do not have sufficient privileges for this operation!',
        message: '',
        color: 'red.9',
        icon: <BiErrorAlt />
      })
      break;
    case 500:
      notifications.show({
        title: responseData.msg,
        message: '',
        autoClose: false,
        withCloseButton: true,
        color: 'red.9',
        icon: <BiErrorAlt />
      })
      break;
  }
}

export function ErrorNotification(title, msg='') {
  notifications.show({
    title: title,
    message: msg,
    color: 'red.9',
    icon: <BiErrorAlt />
  })
}
