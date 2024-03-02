import sha256 from 'crypto-js/sha256'

document.querySelectorAll('input.confirmation-code-input[data-hash').forEach(
    (input) => {
        const storedHash = input.getAttribute('data-hash')

        input.addEventListener('input',
            (e) => {
                const hashedValue = sha256(input.value).toString()

                if (hashedValue === storedHash) {
                    input.form.submit()
                }
            }
        )
    }
)
