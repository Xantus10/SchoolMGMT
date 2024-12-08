
export function checkNullArray(arr) {
  return (!(arr) || arr.length === 0);
}

export function constructClassId(course, year, group) {
  let now = new Date()
  now.setMonth(now.getMonth()-8)
  return `${course}${now.getFullYear()-year+1}${(group === null) ? '' : c[3]}`
}
