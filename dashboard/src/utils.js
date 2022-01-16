export function getPlaceStatus(percentage) {
    if (percentage < 0.3) {
        return { text: 'Relatively empty', bg: 'success' }
    } else if (percentage < 0.8) {
        return { text: 'Moderately full', bg: 'warning' }
    } else {
        return { text: 'Full', bg: 'danger' }
    }
}

