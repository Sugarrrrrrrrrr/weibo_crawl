

if __name__ == '__main__':

    ls = ['log_2018-08-28_1535443804.txt',
          'log_2018-08-28_1535448367.txt'
        ]

    f_o = open(ls[0], 'a', encoding='utf-8')
    for f_name in ls[1:]:
        with open(f_name, 'r', encoding='utf-8') as f:
            for line in f:
                f_o.write(line)

    f_o.close()
                
