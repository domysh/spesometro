import { Input, InputProps, PolymorphicComponentProps } from '@mantine/core'
import Big from 'big.js'
import { ChangeEvent, useState } from 'react'
import MaskedInput, { MaskedInputProps } from 'react-text-mask'
import createNumberMask from 'text-mask-addons/dist/createNumberMask'

export type MaskOptions = {
  prefix?: string
  suffix?: string
  includeThousandsSeparator?: boolean
  thousandsSeparatorSymbol?: string
  allowDecimal?: boolean
  decimalSymbol?: string
  decimalLimit?: number
  integerLimit?: number
  allowNegative?: boolean
  allowLeadingZeroes?: boolean
}

const defaultMaskOptions:MaskOptions = {
  prefix: '',
  suffix: '',
  includeThousandsSeparator: true,
  thousandsSeparatorSymbol: '',
  allowDecimal: true,
  decimalSymbol: ',',
  decimalLimit: 2, // how many digits allowed after the decimal
  integerLimit: 7, // limit length of integer numbers
  allowNegative: false,
  allowLeadingZeroes: false,
}

type AdvancedNumberInputProps = 
  Omit<{ maskOptions?: MaskOptions } & Omit<PolymorphicComponentProps<MaskedInput, InputProps> & Omit<MaskedInputProps, "mask">, "component">, "onChange"> & { onChange: (value:Big) => void }

export const AdvancedNumberInput = ({ maskOptions, ...inputProps }: AdvancedNumberInputProps ) => {

  const finalMaskOptions = {
    ...defaultMaskOptions,
    ...(maskOptions??{})
  }

  const currencyMask = createNumberMask(finalMaskOptions)

  const [lastIntegerWasZero, setLastIntegerWasZero] = useState(false)

  const customOnChange = (e:ChangeEvent<HTMLInputElement>) => {
    if (inputProps.onChange == null) return
    
    const value = (e.target.value??(finalMaskOptions.prefix+"0"+finalMaskOptions.suffix))
    const extractedInput = value.substring(finalMaskOptions.prefix?.length??0, value.length-(finalMaskOptions.suffix?.length??0))
    const transformedInput = extractedInput.replace(finalMaskOptions.thousandsSeparatorSymbol??'', '').replace(finalMaskOptions.decimalSymbol??'', '.')
    let finalnum = Big(0)
    try{finalnum = Big(transformedInput)}catch(e){}
    const integerPart = finalnum.round(0, Big.roundDown)
    if (lastIntegerWasZero && !integerPart.eq(0)){
      finalnum = finalnum.sub(integerPart.sub(integerPart.div(10)))
    }
    setLastIntegerWasZero(integerPart.eq(0))
    inputProps.onChange(finalnum)
  }

  return <Input
    component={MaskedInput}
    mask={currencyMask}
    {...inputProps}
    onChange={customOnChange}
  />
}
