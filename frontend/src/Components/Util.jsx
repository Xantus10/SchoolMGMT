
export function checkNullArray(arr) {
  return (!(arr) || arr.length === 0);
}

export function constructClassId(course, year, group) {
  let now = new Date()
  now.setMonth(now.getMonth()-8)
  return `${course}${now.getFullYear()-year+1}${(group === 0) ? '' : group}`
}

export function stampToTime(timestamp) {
  let hours=Math.floor(timestamp/60).toString(), mins=(timestamp%60).toString()
  return hours + ':' + (mins.length === 1 ? '0' : '') + mins
}
